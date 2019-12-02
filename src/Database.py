import sqlite3

class sqlite():
	'''
	The service provider for an SQLite3 file based database
	'''

	db_type = None
	dbms = None

	def __init__(self, dbms=None):
		try:
			self.db_type = 'sqlite3'
			if not dbms:
				dbms = ':memory:'
			self.dbms = dbms
			self.cx = sqlite3.connect(dbms)
			self.cx.row_factory = self.dictFactory

		except Exception as e:
			print( "%s" % e )

	def dictFactory(self,cur,row):
		rv = {}
		ix = 0
		for t in cur.description:
			tag = t[0]
			rv[tag] = row[ix]
			ix += 1

		return rv

	def type(self):
		return self.db_type

	def database(self):
		return self.dbms

	def table_list_query(self):
		return "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'";

	def variable_list_query(self, table):
		pass


class DatabaseError(Exception):
	'''
	Database error class
	'''
	pass

class Database():
	'''
	Generic database interface for a quick and dirty persistence
	model, suitable for Raspberry Pi, and docker implementations.
	'''

	provider = None
	def __init__(self, provider=None):
		if provider:
			self.provider = provider
		else:
			raise DatabaseError('Database connection problem')

	def type(self):
		return self.provider.type()

	def database(self):
		return self.provider.database()

	def close(self):
		self.cx.close()
		
	def cursor(self):
		return self.provider.cx.cursor()

	def commit(self):
		self.provider.cx.commit()

	def query(self,query ):
		cur = self.cursor()
		cur.execute( query )
		return cur

	def dropTable(self, table):
		self.query( 'drop table if exists %s;' % table )

	def varType(self, s):
		if isinstance( s, int):
			return 'integer'
		if isinstance( s, float):
			return 'float'
		if isinstance( s, str):
			return 'varchar(%d)' % len(s) 

	def isString(self, v ):
		if isinstance( v, str ):
			return True
		return False

	def tableFromDict(self, table, dct ):
		q = 'create table %s (\n' % table
		for k in dct.keys():
			q += '  %s %s,\n' % (k,self.varType(dct[k]))
		q = q[0:-2] + '\n);'
		return q

	def insertFromDict(self, table, dct ):
		n = len(dct.keys())
		q = 'INSERT INTO %s (' % table 
		q += ','.join( dct.keys() )
		q +=  ') VALUES( '
		q += '?,' * n
		q = q[0:-1]
		q += ' );'
		return q

	def persistDict(self, table, dlst ):
		q = self.insertFromDict( table, dlst[0] )
		c = self.cursor()
		try:
			tlst = self.dlistToTuples( dlst )
			c.executemany(q,tlst)
		except Exception as e:
			print( ":::: insertion error:", e, q, tlst )

	def dlistToTuples(self, dlst ):
		rv = []
		for d in dlst:
			new = '('
			for k in d.keys():
				v = d[k]
				if self.isString( v ):
					new += "'%s'," % d[k]
				else:
					new += "%s," % d[k]
			new += ')'
			rv.append( eval( new ) )
		return rv

	def variables(self, table, qualified = False):
		q = "select * from %s limit 1;" % table
		cur = self.query( q )
		row = cur.fetchone()
		if qualified:
			rv = []
			for v in row.keys():
				rv.append( '%s.%s' % (table,v) )
			return rv

		return row.keys()

	def tables(self):
		rv = []
		q = self.provider.table_list_query()
		for t in self.query( q ):
			rv.append( t['name'] )
		return rv

	def __iter__(self):
		pass


if __name__ == '__main__':

	provider = sqlite( dbms='mydb.sq3')
	db = Database(provider)
	
	dl = [
		{ 'id': 0, 'tag': 'Zero' },
		{ 'id': 1, 'tag': 'One' },
		{ 'id': 2, 'tag': 'Two' },
		{ 'id': 3, 'tag': 'Three' },
		{ 'id': 4, 'tag': 'Four' },
		{ 'id': 5, 'tag': 'Five' },
	]
	
	x = db.tableFromDict( 'xyzzy', dl[0] )
	db.dropTable('xyzzy')
	db.query(x)

	y = db.tableFromDict( 'myzzy', dl[0] )
	db.dropTable('myzzy')
	db.query(y)

	x = db.persistDict( 'xyzzy', dl )
	y = db.persistDict( 'myzzy', dl )
	db.commit()
	
	c = db.cursor()
	print( "Query:" )
	for d in c.execute( 'select * from xyzzy;'):
		print(d)

	print( "Tables:" )
	for t in db.tables():
		print(t)
		for v in db.variables( t, qualified = False ):
			print( "  %s" % v )	
	db.close()	
