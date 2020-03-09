import os
from passlib.hash import sha256_crypt as crypto
from Database import Sqlite, Database

class userException(Exception):
	pass

class Users:

	location='../data'
	database='users.db'
	table='user_table' 
	database = os.path.join( location, database )
	print( database )
	db=None

	def __init__(self):
		provider = Sqlite( dbms = self.database )
		self.db = Database(provider)

	def hash(self,clear):
		return crypto.encrypt(clear)

	def validate(self,clear,hash):
		return crypto.verify(clear,hash)

	def confirm(self,dct):
		if 'email' in dct:
			if 'confirm' in dct:
				if dct['email'] != dct['confirm']:
					raise userException( 'Email Mismatch.' )

		if 'password' in dct:
			if 'password2' in dct:
				if dct['password'] != dct['password2']:
					raise userException( 'Password Mismatch.' )

		return True

	def registry(self, dct):
		if self.confirm( dct ):
			return {
				'user': dct['username'],
				'email': dct['email'],
				'admin': False,
				'password': self.hash( dct['password'] )
			}

		return {}

	def register(self, udct ):

		persist = self.registry( udct )
		tlist = self.db.tables()
		if not self.table in self.db.tables():
			q = self.db.tableFromDict(self.table, persist)
			self.db.dropTable(self.table)
			self.db.query(q)
			self.db.query( 'CREATE UNIQUE INDEX %s_ix ON %s(email)' % (self.table,self.table))

		q = self.db.insertFromDict(self.table, persist)
		return self.db.persistDict(self.table, [persist])

	def lookup(self,info):
		q = "select * from %s where email = '%s';" % (self.table,info['email'])
		cur = self.db.query(q)
		if cur:
			return cur.fetchone()

		return None

	def user(self, usr ):
		q = "select * from %s where user = '%s';" % (self.table,usr)
		cur = self.db.query(q)
		if cur:
			return cur.fetchone()

		return None



	def login(self,info):
		account = self.lookup(info)
		if not account:
			raise userException( 'No such user, please register' )

		if account and self.validate( info['password'], account['password']):
			return True

		raise userException( 'Password mismatch' )

	def list(self, email=None):
		if email:
			cursor = self.db.query( "select * from %s where email = '%s';" % (self.table,email))
		else:
			cursor = self.db.query( "select * from %s ;" % self.table)

		return cursor.fetchall()


	def delete(self, **kwargs ):
		pass

if __name__ == '__main__':

	usr = Users()
	usr.register( { 'username': 'rob', 'password': 'xyzzy' } )
