import smbus

class i2cBus():

	def __init__( self, bus ):
		try:
			self.bus = smbus.SMBus( bus )
		except Exception as e:
			print( 'unable to create i2c bus %d: %s' % (bus,e) )

	def interrogate( self ):
		rv = []
		for device in range( 128 ):
			try:
				ch = self.bus.read_byte( device )
				rv.append( hex( device ) )
			except Exception as e:
				pass
		return rv


if __name__ == '__main__':

	bus = i2cBus( 1 )

	print( bus.interrogate() )
