import os
import sys
import datetime
from dateutil.parser import parse
from dateutil.tz import UTC

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Depends
## from fastapi.security import OAuth2PasswordBearer

log = Log( 'ChooChoo' )
api = FastAPI()

timr = None
agg = None
query = None

def initialize():
	pass

@api.get( '/turnouts/v0/create/{tag}')
def create( tag: str ):
	pass


@api.get( '/turnouts/v0/delete/{tag}') 
def delete( tag: str ):
	pass

if __name__ == '__main__':

	log = Log( sys.argv[0] )
	api.run( host = '0.0.0.0', port = 8888, debug = False )
