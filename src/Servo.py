import time
import Adafruit_PCA9685

##
## a class to control the PCA_9685 PWM servo controller
## 
class PCA_9685():

	max_pulse = 600
	min_pulse = 150
	mid_pulse = int( min_pulse + (max_pulse - min_pulse) / 2 )

	pwm_freq = 60
	pwm_controller = None
	servo_state = []

	## initialize a controller on a bus ...
	def __init__( self, bus, addr ):
		self.bus = bus
		self.address = addr
		self.pwm_controller = Adafruit_PCA9685.PCA9685( address = addr, busnum = bus )
		self.pwm_controller.set_pwm_freq( self.pwm_freq )
		for servo in range( 16 ):
			new = {
				'n': servo, 
				'n_states': 2, 
				'state': 0, 
				'pulse': [ self.min_pulse, self.max_pulse ],
			}
			self.servo_state.append( new )
			self.set_neutral( servo )

	## clear the state value of servo N ...
	def clr_state( self, n ):
		self.servo_state[n]['state'] = 0

	## set the servo to the MIDDLE of its travel ...
	def set_neutral( self, n ):
		self.set_raw( n, self.mid_pulse )

	## toggle state and move the servo ...
	def set_toggle( self, n ):
		self.servo_state[n]['state'] = 1 - self.get_state( n )
		self.set_position( n )

	## get the state ... 
	def get_state( self, n ):
		return self.servo_state[n]['state']

	## set the state ... 
	def set_state( self, n, state ):
		d = self.servo_state[n]
		if state < d['n_states']:
			self.servo_state[n]['state'] = state
		else:
			print( 'cannot set state %d: %d' %(n,state))

	## get the current state pulse value ...
	def get_pulse( self, n ):
		d = self.servo_state[n]
		s = d['state']
		p = d['pulse']
		return p 

	## set the position of the servo to the current state ...
	def set_position( self, n ):
		d = self.servo_state[n]
		unit = n
		state = d['state']
		pulse = d['pulse'][state]
		self.set_raw( n, pulse )

	## set the pulse value to the register ...
	def set_raw( self, servo, pulse ):
		self.pwm_controller.set_pwm( servo, 0, pulse )

	## set a tag on a register number ...
	def set_tag( self, servo, tag ):
		d = self.servo_state[servo]
		d['tag'] = tag 

	## toggle the tagged unit ...
	def toggle_tag( self, tag ):
		ix = 0
		for d in self.servo_state:
			if d['tag'] == tag:
				self.set_toggle( ix )
			ix += 1

	## set all servos to state [0:1] ...
	def set_all( self, state ):
		for i in range( len( self.servo_state ) ):
			self.set_state( i, state )

	## set all servos to neutral ... 
	def set_configure( self ):
		for i in range( len( self.servo_state ) ):
			self.set_neutral( i )
				

if __name__ == '__main__':

	tags = [ 
		'zero', 'One', 'Two', 'Three', 
		'Four', 'Five', 'Six', 'Seven', 
		'Eight', 'Nine', 'Ten', 'Eleven', 
		'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
	]

	c = PCA_9685( 1, 0x40 )
	ix = 0
	for t in tags:
		c.set_tag( ix, t )
		ix += 1

	for s in c.servo_state:
		print( s )

	c.set_configure()
	time.sleep( 5 )

	c.toggle_tag( 'Four' ) 
	time.sleep( 5 )

	state = 0
	while True:
		for s in [ 0, 4, 8 ]:
			c.set_toggle( s )

		state = 1 - state
		time.sleep( 1.5 ) 

