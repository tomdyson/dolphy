import unittest
from dolphy import *
import os

class IndexCreation(unittest.TestCase):
	
	def testCreateEmptyIndex(self):
		
		TESTINDEX = '/tmp/dolphy-testindex.db'
		"""A new index file should be created if it didn't exist before"""
		try:
			os.remove(TESTINDEX)
		except OSError:
			pass
		i = Index(TESTINDEX)
		self.assert_(os.path.exists(TESTINDEX))

class IndexManipulation(unittest.TestCase):
	
	def testSingleDocumentAddition(self):
		pass
		
if __name__ == "__main__":
    unittest.main()