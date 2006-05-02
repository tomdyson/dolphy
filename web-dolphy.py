#!/usr/bin/python2.3

import web
import dolphy
import time

web.internalerror = web.debugerror

urls = (
	'/search', 'Results'
)

class Results:
	def GET(self):
		web.header('Content-Type', 'text/html')
		query = web.input().get('q')
		start = time.time()
		i = dolphy.Index('data/test.db')
		results = i.search(query)
		duration = "%.6f" % (time.time() - start)
		tmp = open('templates/results.html').read()
		web.render(tmp, isString=True)

if __name__ == "__main__": web.run(urls)
