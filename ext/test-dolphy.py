import unittest
import dolphy
import os

EMPTYINDEX = '/tmp/dolphy-testindex.db'

class IndexCreation(unittest.TestCase):
	
	def testCreateEmptyIndex(self):
		"""A new index file should be created if it didn't exist before"""
		try:
			os.remove(EMPTYINDEX)
		except OSError:
			pass
		i = dolphy.Index(EMPTYINDEX)
		i.close()
		self.assert_(os.path.exists(EMPTYINDEX))

class IndexManipulation(unittest.TestCase):
	
	def setUp(self):
		"""Create an index with a single known entry"""
		try: os.remove(EMPTYINDEX)
		except OSError: pass
		URI = 'test1.txt'
		title = 'Test 1'
		author = 'Tom'
		modified = 1146593534
		content = 'The cow says moo'
		d = dolphy.Document(URI, title, author, modified)
		d.raw_content = content
		d.tokens = {'The':[0], 'cow':[1], 'says':[2], 'moo':[3]}
		d.length = 4
		i = dolphy.Index(EMPTYINDEX)
		i.add(d)
		i.close()
		
	def tearDown(self):
		"""Remove index detritus"""
		try: os.remove(EMPTYINDEX)
		except OSError: pass		
		
	def testDocumentRetrieval(self):
		i = dolphy.Index(EMPTYINDEX)
		results = i.search('cow')
		self.assertEquals(len(results), 1)
		
if __name__ == "__main__":
    unittest.main()