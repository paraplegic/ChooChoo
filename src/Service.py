import os
import sys
import operator
import datetime
from dateutil.parser import parse
from dateutil.tz import UTC

from sql import Sql
from Logger import Log
from Timing import Timer
from Aggregate import Aggregate

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

log = Log( 'ChooChoo' )
api = FastAPI()

timr = None
agg = None
query = None

def initialize():
	pass

@api.get( '/turnouts/v0/applications/{id}/states/current/formats/timeline')
def timeline( id: int, token: str = Depends( oauth2_bearer ) ):

	s = status( id )
	if 'http_status' in s and s['http_status'] != 200:
		return { 'errors': 'No application id = %d' % id, 'http_status': s['http_status'], 'timeline': None }

	if not 'status' in s:
		log.error( s )
		return { 'errors': 'No application status returned for id = %d' % id, 'http_status': s['http_status'], 'timeline': None }

	new = filter_dates( s['status'] )
	if len( new ) > 0:
		srted = []
		for d in sorted( new, key=new.get ):
			srted.append( { d: new[d] } )

		## this snippet is necessary to support a MOCKING test
		id = None
		if 'AppID' in s['status']:
			id = s['status']['AppID']
		elif 'AppId' in s['status']:
			id = s['status']['AppId']
		else:
			id = s['status']['appid']

		step = None
		if  'Step' in s['status']:
			step = s['status']['Step']
		else:
			step = s['status']['step']

		return { 'errors': None, 'http_status': 200, 'status': { 'AppId': id, 'Step': step, 'timeline': srted } }

	log.error( s )
	return { 'errors': 'There was one', 'http_status': 404, 'timeline': None }


@api.get( '/applications/v0/applications/{id}/states/current')
def status( id: int, token: str = Depends( oauth2_bearer ) ):
	global log
	global query
	global timr
	global agg

	if not query:
		query = initialize()

	if not timr:
		timr = Timer()

	if not agg:
		agg = Aggregate( logger = log, metric = 'Query time', units = 'milliseconds', limit = 10 )

	timr.start()
	rv = query.get_summary( id ) 
	timr.stop()
	agg.observation( timr.millis() )

	if rv:
		return { 'error': None, 'http_status': 200, 'status': rv }

	if query.unavailable:
		raise HTTPException( status_code = 503, detail = 'Service temporarily unavailable' )
		return None

	status = 'Application id %d not found.' % id
	rv = { 'error': status, 'http_status': 404, 'status': None }
	raise HTTPException( status_code = 404, detail = status )
	return rv


if __name__ == '__main__':

	log = Log( sys.argv[0] )
	api.run( host = '0.0.0.0', port = 8888, debug = False )
