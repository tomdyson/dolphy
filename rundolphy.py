from dolphy import *
import re

def testIndex():
	i = Index('data/test.db')
	t = Text()
	strip_tags = re.compile('<.*?>')
	strip_comments = re.compile('<!--.*?-->')
	# add documents to the index
	docs = marshal.loads(open('data/posts.marshal').read())
	start = time.time()
	for doc in docs:
		title = doc[0]
		contents = doc[2]
		epoch_date = doc[1]
		d = Document(title, title, 'Tom', epoch_date)
		# tags and comments should have been stripped already
		contents = strip_comments.sub('',contents)
		d.raw_data = strip_tags.sub('',contents) 
		stream = t.tokenizeAndStem(title + ' ' + contents)
		d.tokens, d.length = t.calculateTokens(stream)
		i.add(d)
	i.close()
	took = time.time() - start
	print "indexed %s docs in %.3f seconds" % (len(docs), took)
	print "(%.2f docs per second)" % (len(docs) / took)
	
def testUnicodeIndex():
	i = Index('data/unicode.db')
	t = Text()
	unicode_text = u'This is the end of the world'
	stream = t.tokenizeAndStem(unicode_text)
	calculated_tokens = t.calculateTokens(stream)
	d = Document(u'unicode doc', u'unicode doc', 'Tom')
	d.tokens = calculated_tokens
	i.add(d)
	
def testSearch(term, summariser='simple'):
	# search the index
	i = Index('data/test.db')
	print '\nSearching for %s...' % term
	start = time.time()
	results = i.search(term, summariser)
	took = time.time() - start
	for result in results:
		print result['title'], result['score']
		print result['summary']
	print "search took %.6f seconds" % (took)

def testSortByDate(term):
	# search the index
	i = Index('data/test.db')
	i.sort_by = i.sortByDate
	print '\nSort by Date.\n\nSearching for %s...' % term
	start = time.time()
	results = i.search(term)
	took = time.time() - start
	for result in results:
		print result['title'], result['score']
		print result['summary']
	print "search took %.6f seconds" % (took)

def testStats():	
	# get stats on the top terms
	i = Index('data/test.db')
	top_terms = []
	for key in [key for key in i.db.keys() if key.startswith('T_')]:
		top_terms.append((len(marshal.loads(i.db[key])), key.replace('T_','')))
	top_terms.sort(); top_terms.reverse()
	for term in top_terms[0:30]:
		print term

if __name__ == "__main__":
	testIndex()
	testSearch('loveday')
	#testSortByDate('music')
	#testStats()