class Table():

	def __init__(self):
		pass

	def entabulate(self, dlist):
		rv = [
			'<div class="table-responsive">',
			'<table class="table table-striped">',
		]
		keys = dlist[0].keys()

		rv.append('<thead>')
		for k in keys:
			rv.append('<td>%s</td>'%k.capitalize())
		rv.append('</thead>')
		for d in dlist:
			rv.append('<tr>')
			for k in keys:
				if k in 'password':
					rv.append('<td>%s</td>'%'*****')
				else:
					rv.append('<td>%s</td>'%d[k])
			rv.append('</tr>')

		rv.append('</table>')
		rv.append('</div>')
		return self.stringify(rv)

	def stringify(self, slist ):
		rv = ''
		for s in slist:
			rv += str( s )
		return rv
