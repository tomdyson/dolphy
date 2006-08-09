import sys; sys.path.append('/Users/tomdyson/Documents/code/python/')

from dolphy.indexer import Index
from dolphy.text import Text
from dolphy.document import Document

import unittest
import os

SIMPLEINDEX = '/tmp/dolphy-testindex.db'

class IndexCreation(unittest.TestCase):
	
	def testCreateSIMPLEINDEX(self):
		"""A new index file should be created if it didn't exist before"""
		try: os.remove(SIMPLEINDEX)
		except OSError: pass
		i = Index(SIMPLEINDEX)
		i.close()
		self.assert_(os.path.exists(SIMPLEINDEX))

class SearchTests(unittest.TestCase):
	
	def setUp(self):
		"""Create an index with a single known entry"""
		try: os.remove(SIMPLEINDEX)
		except OSError: pass
		uri = 'test1.txt'
		modified = 1146593534
		content = 'The cow says moo'
		d = Document(uri, modified)
		d.title = 'Cow speech'
		d.author = 'Tom Dyson'
		d.raw_content = content
		d.tokens = {'The':[0], 'cow':[1], 'says':[2], 'moo':[3]}
		d.my_custom_attribute = 42
		d.length = 4
		self.i = Index(SIMPLEINDEX)
		self.i.add(d)
		
	def tearDown(self):
		"""Remove index detritus"""
		try: self.i.close()
		except: pass
		try: os.remove(SIMPLEINDEX)
		except OSError: pass		
		
	def testSingleTermQuery(self):
		results = self.i.search('cow')
		self.assertEquals(len(results.hits), 1)

	def testTwoTermUnionSuccessQuery(self):
		"""'OR' queries with one matching term and one non-matching should return one document"""
		results = self.i.search('cow q1w2e3r4', operator="OR")
		self.assertEquals(len(results.hits), 1)

	def testTwoTermUnionFailureQuery(self):
		"""'OR' queries with two non-matching terms should return zero documents"""
		results = self.i.search('c1e2d q1w2e3r4', operator="OR")
		self.assertEquals(len(results.hits), 0)

	def testTwoTermIntersectionSuccessQuery(self):
		"""'AND' queries with two matching terms should return one document"""
		results = self.i.search('cow moo', operator="AND")
		self.assertEquals(len(results.hits), 1)
		
	def testThreeTermIntersectionFailureQuery(self):
		"""'AND' queries with one non-matching term and multiple matching terms 
			should return zero documents"""
		results = self.i.search('cow q1w2e3r4 moo', operator="AND")
		self.assertEquals(len(results.hits), 0)
		
	def testTwoTermIntersectionFailureQuery(self):
		"""'AND' queries with one non-matching term and one matching term 
			should return zero documents"""
		results = self.i.search('cow q1w2e3r4', operator="AND")
		self.assertEquals(len(results.hits), 0)
				
	def testCustomAttributeRetrieval(self):
		results = self.i.search('cow')
		self.assertEquals(results.hits[0].my_custom_attribute, 42)
		
	def testZeroDocumentsReturned(self):
		"""Single non-matching term should return zero documents"""
		results = self.i.search('q1w2e3r4t5')
		self.assertEquals(len(results.hits), 0)
		
if __name__ == "__main__":
    unittest.main()