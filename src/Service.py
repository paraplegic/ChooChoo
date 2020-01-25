import os
import sys
import jwt
import json
import datetime
import urllib.parse
from dateutil.parser import parse
from dateutil.tz import UTC

from fastapi import FastAPI, Form, Body
from fastapi import Depends

from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from Users import Users
from Table import Table
from i2cBus import i2cBus
from Servo import PCA_9685

SECRET='ThisDog can Hunt!'
VERSION=0.9

api = FastAPI('Turnout', template_folder='../static')
templates = Jinja2Templates(directory="../templates")
users = None
bus = None
servo_cache = {}


def urltodict( url ):
	rv = {}
	if not url or len(url)== 0:
		return rv

	for pair in url.decode().split('&'):
		x = pair.split('=')
		rv[x[0]] = urllib.parse.unquote_plus(x[1])
	return rv

def initialize( app ):
	app.mount( "/static", StaticFiles(directory="../static"), name="static")

@api.middleware('http')
async def before(request: Request, callback):
	global users, SECRET
	if not users:
		users = Users()

	if 'X-JWT-Token' in request.cookies:
		token = request.cookies['X-JWT-Token']
		if token and len(token) > 0:
			usr = jwt.decode( token, SECRET, algorithms = ['HS256'])
			return await callback(request)

	if request['path'] in ['/login', '/auth', '/register', '/index' ]:
		return await callback(request)

	return RedirectResponse(url='/login')

@api.post( '/login')
def plogin(request: Request):
	return login(request)

@api.get( '/login')
def login( request: Request ):
	global VERSION
	context = { 
		'request': request, 
		'app': 'Turnout', 
		'version': VERSION
	}
	return templates.TemplateResponse('login.html',context)

@api.post( '/index')
def pindex(request: Request):
	return index(request)

@api.get( '/index')
def index( request: Request):
	global VERSION
	context = {
		'request': request,
		'app': 'Turnout',
		'version': VERSION,
	}
	x = templates.TemplateResponse('index.html',context)
	return x

@api.get( '/register')
def register( request: Request ):
	global VERSION
	context = { 
		'request': request, 
		'app': 'Turnout', 
		'version': VERSION
	}
	return templates.TemplateResponse('register.html',context)

@api.get( '/logout')
def logout( request: Request ):
	global VERSION
	context = { 
		'request': request, 
		'app': 'Turnout', 
		'version': VERSION
	}
	response = RedirectResponse( url = '/login' )
	response.delete_cookie(key='X-JWT-Token')
	return response

@api.post( '/auth' )
async def auth( request: Request ):
	global users, SECRET

	u = None
	rv = False
	rqst = await request.body()
	response = Response( content = 'login failed.', status_code = 401 )
	try:
		usr = urltodict( rqst )
		if 'confirm' in usr:
			rv = users.register( usr )
			response = RedirectResponse( url = '/login' )
		else:
			try:
				rv = users.login( usr )
				u = users.lookup( usr )
				token = jwt.encode(u, SECRET, algorithm="HS256")
				response = RedirectResponse( url = '/index' )
				response.set_cookie(key='X-JWT-Token', value = str(token, encoding='utf-8'), httponly = True )
				return response

			except Exception as e:
				print('EXCEPTION: ',e)
		
	except Exception as e:
		print('EXCEPTION:',e)

	return response

@api.get('/administer')
def get_users(request: Request):
	global users, VERSION
	context = {
		'request': request,
		'app': 'Turnout',
		'version': VERSION,
		'table': None
	}
	context['table'] = Table().entabulate(users.list())
	return templates.TemplateResponse('administer.html',context)

@api.get( '/controller')
def servo(request: Request):
	global bus
	context = {
		'request': request,
		'app': 'Turnout',
		'version': VERSION,
		'i2cBus': None
	}

	if not bus:
		bus = i2cBus(1)

	servo_list = bus.interrogate()

	context['i2cList'] = servo_list
	return templates.TemplateResponse('controller.html',context)

@api.post( '/servos')
async def servos(request: Request):
	global bus,servo_cache
	context = {
		'request': request,
		'app': 'Turnout',
		'version': VERSION,
		'i2cBus': None,
		'controller': None
	}

	if not bus:
		bus = i2cBus(1)

	rqst = await request.body()
	r = urltodict( rqst )

	addr = r['controller']
	context['i2cList'] = bus.interrogate()
	context['controller'] = addr
	
	if not addr in servo_cache: 
		servo_cache[addr] = PCA_9685(1, int(addr,0))

	state = servo_cache[addr].servo_state
	context['servos'] = state
	print( state )
	return templates.TemplateResponse('servos.html',context)

@api.get( '/turnout') 
def turnout(request: Request):
	global users, VERSION
	context = {
		'request': request,
		'app': 'Turnout',
		'version': VERSION,
	}

	return templates.TemplateResponse('turnout.html',context)

@api.get( '/siding') 
def siding(request: Request):
	pass

if __name__ == '__main__':

	templates = initialize( api )
	api.run( host = '0.0.0.0', port = 8888, debug = True )
