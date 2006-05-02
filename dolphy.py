# Dolphy - high performance, pure Python text indexer
# Tom Dyson, April 2006

# TODO: match Documents to numerical IDs
# TODO: Phrase searching
# TODO: Boolean queries
# TODO: HTTP interface
# TODO: Improve summarisation performance

import re
from nltk_lite import tokenize
import time
import dbhash
import marshal

STOPWORDS = '/Users/tomdyson/Documents/code/python/dolphy/data/stopwords.txt'

class Index:
	
	"""
		A persisted hash of terms and documents
		T_foo = {doc_1:[position_1, position_2], doc_2:[position_1]}
		D_doc_1 = {uri:URI, title:Title, author:Author, 
			modified:Modification Date, tokens: Tokens, raw: Raw content}
	"""
	
	def __init__(self, filename):
		self.filename = filename
		self.db = dbhash.open(self.filename, flag='c')
		self.sort_by = self.sortByPositionAndFrequency
		
	def add(self, document, defer_recalculate = True):
		# Add an entry for each document's metadata
		doc_details = {}
		doc_details['uri'] = document.uri
		doc_details['title'] = document.title
		doc_details['author'] = document.author
		doc_details['modified'] = document.modified
		modified = time.localtime(document.modified)
		doc_details['str_modified'] = time.strftime('%d %B %Y', modified)
		try:
			# TODO: better name for raw_content
			# TODO: check attribute exists, don't just try to read it
			doc_details['raw_content'] = document.raw_data
		except AttributeError:
			pass
		self.db["D_" + document.uri.encode('utf-8')] = marshal.dumps(doc_details)
		# Add/update the entry for each term in the document
		for term in document.tokens:
			if self.db.has_key('T_' + term):
				term_data = marshal.loads(self.db['T_' + term])
				term_data[document.uri] = (document.tokens[term], document.length)
			else:
				term_data = {}
				term_data[document.uri] = (document.tokens[term], document.length)
			self.db['T_' + term] = marshal.dumps(term_data)
		
	def remove(self, document_URI, defer_recalculate = True):
		pass
		
	def update(self, document, defer_recalculate = True):
		pass
		
	def recalculate(self):
		pass
		
	def sortByPositionAndFrequency(self, documents):
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
			doc_details = marshal.loads(self.db['D_' + doc])
			results.append((doc_details['modified'], doc))
		results.sort()
		results.reverse()
		return results

	def search(self, query):
		query = query.lower()
		ret = []
		t = Text()
		porter = tokenize.PorterStemmer()
		stemmed_query = porter.stem(query)
		matching_documents = self.db.get('T_' + stemmed_query)
		if matching_documents:
			documents = marshal.loads(matching_documents)
			results = self.sort_by(documents)
			ret = []
			for result in results:
				doc = marshal.loads(self.db['D_' + result[1]])
				doc['score'] = result[0]
				if doc.get('raw_content'):
					doc['summary'] = t.summarise(doc['raw_content'], query)
				else:
					doc['summary'] = ''
				ret.append(doc)
		return ret

class Document:
	
	"""
		Dolphy documents have six properties:
			URI - typically file location or URL
			Title - typically extracted from source metadata
			Author
			Modification date - seconds since the epoch
			Tokens - a dict of term:positions ({'foo':[3,5],})
			Raw content for summaries
	"""

	def __init__(self, uri, title="", author="", modified=0):
		self.uri = uri
		self.title = title
		self.author = author
		# modified should be seconds since epoch, defaults to now
		if int(modified) == modified:
			if modified == 0:
				modified == int(time.time())
			self.modified = modified
		else:
			raise "'modified' should be seconds since the epoch"

class Text:

	def __init__(self):
		# TODO: consider localisation
		self.stopwords = [line.strip() for line in open(STOPWORDS)]
		self.whitespace_splitter = re.compile("\\w+", re.U)
		self.space_or_break = re.compile("\s|\n")
		self.strip_comments = re.compile('<!--.*?-->')
		self.strip_tags = re.compile('<.*?>')
		self.encased_word = re.compile('^\W*(\w+)\W*s?\W?$')
		# TODO: I don't like defining the caching stemmer here
		porter = tokenize.PorterStemmer()
		self.cachingStemmer = Memoize(porter.stem)

	def tokenizeAndStem(self, string):
		"""Yield a stream of downcased words from a string."""
		# crude HTML comment and tag removal
		string = self.strip_comments.sub('',string)
		string = self.strip_tags.sub('',string)
		porter = tokenize.PorterStemmer()
		tokenstream = tokenize.regexp(string, self.whitespace_splitter)
		for token in tokenstream:
			token = token.lower()
			# ignore words with less than three letters,
			# stem words with more than three letters
			if len(token) > 2 and token not in self.stopwords:
				if len(token) == 3:
					yield token
				else:
					stemmed_token = self.cachingStemmer(token)
					yield stemmed_token

	def calculateTokens(self, tokens):
		"""Format tokenised stream into a dict of 
			term:positions plus total tokens ({'foo':[3,5],},10)"""
		dtokens = {}
		position = 1
		for token in tokens:
			if dtokens.get(token):
				dtokens[token].append(position)
			else:
				dtokens[token] = [position]
			position += 1
		return dtokens, position

	def summarise(self, text, term, margin=5, max_phrases=3):
		"""Naive contextual highlighting"""
		tokens = self.space_or_break.split(text)
		position = 0
		phrases = []
		for token in tokens:
			clean_token = token.lower()
			if term in clean_token.lower():
			# v2. try to speed up by using compiled expression 
				matching_word = self.encased_word.search(clean_token)
				if matching_word and matching_word.group(1) == term:
				#v1. if re.search('^\W*(' + term + ')\W*s?\W?$', clean_token):
					before = ' '.join(tokens[position-margin:position])
					after = ' '.join(tokens[position+1:position+margin])
					before = before.split('.')[-1].strip()
					after = after.split('.')[0].strip()
					phrases.append(before + ' <strong>' + token + '</strong> ' + after)				
					if len(phrases) == max_phrases: break
			position += 1
		return ' ... '.join(phrases)

class Cache:
	"""General purpose caching, currently dropped in favour of 
		less functional but less instrusive Memoize"""
	def __init__(self, max_keys = 5000):
		self.max_keys = max_keys
		self._cache = {}
		
	def get(self, key):
		return self._cache.get(key)
		
	def set(self, key, value):
		if len(self._cache) < self.max_keys:
			self._cache[key] = value
		else: pass
	
	def __len__(self): 
		return len(self._cache)
		
	def store(self, filename):
		fo = open(filename, 'w')
		fo.write(marshal.dumps(self._cache))
		fo.close()
		
	def load(self, filename):
		fo = open(filename)
		self._cache = marshal.loads(fo.read())
		fo.close()
		
class Memoize:
	# TODO: include support for pre-loading cached values, like Cache().load()
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}

    def __call__(self, *args):
        if not self.memo.has_key(args):
            self.memo[args] = self.fn(*args)
        return self.memo[args]