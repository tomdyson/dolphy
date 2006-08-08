# Dolphy - high performance, pure Python text indexer
# Tom Dyson, April 2006

# TODO: Phrase searching
# TODO: Boolean queries
# DONE: Paging support
# TODO: Tests

#import sys
#sys.path.append('dolphy/lib')

import dolphy
import time
import dbhash
import marshal
from sets import Set
from lib.nltk_lite import tokenize

class Index(object):
	
	"""
		A persisted hash of terms and documents
		T_foo = {doc_1:[position_1, position_2], doc_2:[position_1]}
		D_doc_1 = {uri:URI, title:Title, author:Author, 
			modified:Modification Date, str_modified:Readable date,
			tokens: Tokens, raw_content: Raw content}
	"""
	
	def __init__(self, filename, flag='c'):
		self.filename = filename
		self.db = dbhash.open(self.filename, flag)
		self.max_id = int(self.db.get('M_max_id', 0))
		self.sort_by = self.sortByPositionAndFrequency
		# TODO: consider requirement for loading stopwords here
		# or speed it up
		self.stopwords = [line.strip() for line in open(dolphy.STOPWORDS)]
	
	def add(self, document, defer_recalculate = True):
		# Retreive (if known URI) or assign document ID
		known_ID = self.db.get('U_'+ document.uri)
		if known_ID:
			document.id = int(known_ID)
		else:
			self.max_id += 1
			self.db['M_max_id'] = str(self.max_id)
			document.id = self.max_id
			self.db["U_" + document.uri] = str(document.id)
		# Add an entry for each document's metadata
		tokens = document.tokens
		del(document.tokens) # we don't want to store these
		doc_details = document.__dict__
		modified = time.localtime(document.modified)
		doc_details['str_modified'] = time.strftime('%d %B %Y', modified)
		self.db["D_%s" % document.id] = marshal.dumps(doc_details)
		# Add/update the entry for each term in the document
		for term in tokens:
			if self.db.has_key('T_' + term):
				term_data = marshal.loads(self.db['T_' + term])
			else:
				term_data = {}
			term_data[document.id] = (tokens[term], document.length)
			# TODO: optimise by chunking db inserts
			self.db['T_' + term] = marshal.dumps(term_data)
		
	def remove(self, document_URI, defer_recalculate = True):
		pass
		
	def update(self, document, defer_recalculate = True):
		pass
		
	def recalculate(self):
		pass
		
	def sortByPositionAndFrequency(self, documents):
		"""Rank documents by term frequency and position"""
		results = []
		for doc in documents:
			score = 0
			positions, length = documents[doc]
			length = float(length)
			# helen's ranking: position 1/x has multiplier 2,
			# position x has multiplier 1
			for position in positions:
				score += (2 * (length - 1)) / (position + length - 2)
			results.append((score, doc))
		results.sort()
		results.reverse()
		return results
		
	def sortByDate(self, documents):
		results = []
		for doc in documents:
			doc_details = marshal.loads(self.db['D_' + str(doc)])
			results.append((doc_details['modified'], doc))
		results.sort()
		results.reverse()
		return results
		
	def mergeMatches(self, doc_groups, merge_type="intersection"):
		"""	Combine sets of matching documents, e.g. for each term
			in a multi-term query. Supports intersections (for AND
			queries) and unions (for ORs). """
		# TODO: less frequent terms (across all documents) should
		# be weighted - perhaps this is where to return the weighting
		# (or just the frequency)
		combined_set = {}
		doc_groups_copy = list(doc_groups)
		intersected = Set(doc_groups_copy.pop().keys())
		if merge_type == "intersection":
			for doc_group in doc_groups_copy:
				intersected = intersected.intersection(Set(doc_group.keys()))
			for doc in intersected:
				positions = []
				len = 0
				for doc_group in doc_groups:
					positions.extend(doc_group[doc][0])
					len = doc_group[doc][1] # should only have to get this once
				combined_set[doc] = (positions, len)
		elif merge_type == "union":
			for doc_group in doc_groups_copy:
				intersected = intersected.union(Set(doc_group.keys()))
			for doc in intersected:
				positions = []
				len = 0
				for doc_group in doc_groups:
					if doc in doc_group:
						positions.extend(doc_group[doc][0])
						len = doc_group[doc][1] # should only have to get this once
				combined_set[doc] = (positions, len)
		return combined_set

	def search(self, query, summarise='simple', page_start=1, page_size=10, operator="AND"):
		"""Retrieve and sort documents containing the specified term(s)"""
		query_terms = query.lower().strip().split(' ')
		ret = []
		t = dolphy.text.Text()
		porter = tokenize.PorterStemmer()
		if len(query_terms) > 1:
			matching_document_groups = []
			for query_term in query_terms:
				if query_term not in self.stopwords:
					stemmed_query = porter.stem(query_term)
					matching_documents = self.db.get('T_' + stemmed_query)
					if matching_documents:
						matching_document_groups.append(marshal.loads(matching_documents))
			# copy the list of matching document groups for sets
			if operator == "AND": join_type = "intersection"
			elif operator == "OR": join_type = "union"
			documents = self.mergeMatches(matching_document_groups, join_type)
		else:
			query_term = query_terms[0]
			stemmed_query = porter.stem(query_term)
			matching_documents = self.db.get('T_' + stemmed_query)
			if matching_documents: # TODO: ugly (check repeated below)
				documents = marshal.loads(matching_documents)
		ret = {'hits':[], 'query': query} # TODO: reconsider (added to protect templates)
		if matching_documents:
			results = self.sort_by(documents)
			ret['count'] = len(results)
			ranked_documents = []
			page_from = page_start - 1
			page_to = page_from + page_size
			for result in results[page_from:page_to]:
				doc = marshal.loads(self.db['D_%s' % result[1]])
				doc['score'] = result[0]
				if doc.get('body'):
					# TODO: dispatch summarisers better
					if summarise == 'highlight':
						doc['summary'] = t.summarise(doc['body'], query)
					else:
						doc['summary'] = t.simpleSummarise(doc['body'])
				else:
					doc['summary'] = ''
				# convert hit dict into a Storage object
				doc = storage(doc)
				ranked_documents.append(doc)
			ret['hits'] = ranked_documents
			# convert results dict into a Storage object
			ret = storage(ret)
		return ret
		
	def close(self):
		self.db.close()
		
class Storage(dict):
    """	A Storage object is like a dictionary except `obj.foo` can be used
    	instead of `obj['foo']`. Create one by doing `storage({'a':1})`.
		From web.py (webpy.org) """
    def __getattr__(self, k): 
        if self.has_key(k): return self[k]
        raise AttributeError, repr(k)
    def __setattr__(self, k, v): self[k] = v
    def __repr__(self): return '<Storage '+dict.__repr__(self)+'>'

storage = Storage