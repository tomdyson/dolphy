"""
Dolphy notes

* Documents have arbitrary attributes and 
 - tokens
  - (converted into a dict of term:positions plus total tokens ({'foo':[3,5],},10))
 - one standard sort relies on date_modified
 - one standard summarisation relies on body

* define stemming/tokeniser on an index (like swish-e) or on a document/query (like lucene)?
"""

# Example indexing API:

i = Index('data/test.db') # possible optimisations in read-only mode?

t = Text()

d = Document()
d.uri = '/the_sun.html'
d.title = 'The warmth of the sun'
d.author = 'Brian Wilson'
d.genres = ['surf','1960s']
d.date_modified = time.gmtime() # python time tuple or seconds since epoch?
d.body = getDocContentsAsString()
d.tokens = t.englishStemmingTokeniser(d.title, d.author, d.body) # or use your own tokeniser
i.add(d)

i.close() # do optimisations here?

# Example searching API:

# simple search
results = i.search('warmth')

# filtering on meta data
def onlySurf(doc): return 'surf' in doc.genres		
results = i.search(query = 'warmth', filter = 'onlySurf')
