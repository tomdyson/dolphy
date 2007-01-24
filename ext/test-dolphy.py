import sys; sys.path.append('/Users/tomdyson/Documents/code/python/')

from dolphy.indexer import Index
from dolphy.text import Text
from dolphy.document import Document

import unittest
import os

SIMPLEINDEX = '/tmp/dolphy-testindex.db'

class IndexManipulation(unittest.TestCase):
	
	def testCreateSIMPLEINDEX(self):
		"""A new index file should be created if it didn't exist before"""
		try: os.remove(SIMPLEINDEX)
		except OSError: pass
		i = Index(SIMPLEINDEX)
		i.close()
		self.assert_(os.path.exists(SIMPLEINDEX))

class SearchTests(unittest.TestCase):
	
	def setUp(self):
		"""Create an index with a two known entries"""
		try: os.remove(SIMPLEINDEX)
		except OSError: pass
		d = Document('test1.txt', 1146593534)
		d.title = 'Cow speech'
		d.author = 'Tom Dyson'
		d.raw_content = 'The cow declares moo'
		d.my_custom_attribute = 42
		d.tokens = {'The':[0], 'cow':[1], 'says':[2], 'moo':[3]}
		d.length = 4
		d2 = Document('test2.txt', 1146593534)
		d2.title = 'Sheep speech'
		d2.author = 'Tom Dyson'
		d2.raw_content = 'The sheep declares baa'
		d2.tokens = {'The':[0], 'bull':[1], 'says':[2], 'moo':[3]}
		d2.length = 4
		self.i = Index(SIMPLEINDEX)
		self.i.add(d); self.i.add(d2)
		
	def tearDown(self):
		"""Remove index detritus"""
		try: self.i.close()
		except: pass
		try: os.remove(SIMPLEINDEX)
		except OSError: pass		
		
	def testSingleTermQuery(self):
		"""Single matching term should return one document"""
		results = self.i.search('cow')
		self.assertEquals(len(results.hits), 1)

	def testSingleTermQuery2(self):
		"""Single matching term should return two documents"""
		results = self.i.search('moo')
		self.assertEquals(len(results.hits), 2)

	def testTwoTermUnionSuccessQuery(self):
		"""'OR' queries with one matching term and one non-matching should return one document"""
		results = self.i.search('cow q1w2e3r4', operator="OR")
		self.assertEquals(len(results.hits), 1)

	def testTwoTermUnionSuccessQuery2(self):
		"""'OR' queries with one matching term should return two documents"""
		results = self.i.search('cow bull', operator="OR")
		self.assertEquals(len(results.hits), 2)

	def testOperatorOverride(self):
		"""Default 'OR' operator should be overridden by 'and' in query"""
		results = self.i.search('cow and bull', operator="OR")
		self.assertEquals(len(results.hits), 0)

	def testOperatorOverride2(self):
		"""Default 'AND' operator should be overridden by 'or' in query"""
		results = self.i.search('cow or bull', operator="AND")
		self.assertEquals(len(results.hits), 2)

	def testTwoTermIntersectionSuccessQuery(self):
		"""'AND' queries with two matching terms should return one document"""
		results = self.i.search('cow moo', operator="AND")
		self.assertEquals(len(results.hits), 1)
		
	def testSingleTermFailureQuery(self):
		"""Single non-matching term should return zero documents"""
		results = self.i.search('q1w2e3r4t5')
		self.assertEquals(len(results.hits), 0)

	def testTwoTermUnionFailureQuery(self):
		"""'OR' queries with two non-matching terms should return zero documents"""
		results = self.i.search('c1e2d q1w2e3r4', operator="OR")
		self.assertEquals(len(results.hits), 0)
		
	def testThreeTermIntersectionFailureQuery(self):
		"""'AND' queries with one non-matching term and multiple matching terms should return zero documents"""
		results = self.i.search('cow q1w2e3r4 moo', operator="AND")
		self.assertEquals(len(results.hits), 0)
		
	def testTwoTermIntersectionFailureQuery(self):
		"""'AND' queries with one non-matching term and one matching term 
			should return zero documents"""
		results = self.i.search('cow q1w2e3r4', operator="AND")
		self.assertEquals(len(results.hits), 0)
				
	def testCustomAttributeRetrieval(self):
		"""Custom attributes should be retrieved"""
		results = self.i.search('cow')
		self.assertEquals(results.hits[0].my_custom_attribute, 42)
		
if __name__ == "__main__":
	index_manipulation_suite = unittest.makeSuite(IndexManipulation)
	unittest.TextTestRunner(verbosity=2).run(index_manipulation_suite)
	search_suite = unittest.makeSuite(SearchTests)
	unittest.TextTestRunner(verbosity=2).run(search_suite)
