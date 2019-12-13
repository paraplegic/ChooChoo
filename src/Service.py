import os
import sys
import datetime
from dateutil.parser import parse
from dateutil.tz import UTC

from fastapi import FastAPI
from fastapi import Depends
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request

VERSION=0.9

api = FastAPI('Turnout', template_folder='../static')
templates = Jinja2Templates(directory="../templates")

def initialize( app ):
	app.mount( "/static", StaticFiles(directory="../static"), name="static")

@api.get( '/')
def healthTest():
	return { 'turnout': 'running', 'version': VERSION } 

@api.get( '/index')
def index( request: Request ):
	return templates.TemplateResponse( 'base.html', { 'request': request, 'app': 'Turnout', 'version': VERSION } )

@api.post( '/register')
def register():
	pass

@api.post( '/login')
def login():
	pass

@api.get( '/servo')
def servo():
	pass

@api.get( '/turnout') 
def turnout():
	pass

@api.get( '/siding') 
def siding():
	pass

if __name__ == '__main__':

	templates = initialize( api )
	api.run( host = '0.0.0.0', port = 8888, debug = True )
