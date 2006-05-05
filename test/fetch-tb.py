import urllib
from BeautifulSoup import BeautifulSoup
import time
import marshal

archives_url = 'http://throwingbeans.org/archives.html'
archives_html = urllib.urlopen(archives_url).read()
soup = BeautifulSoup(archives_html)
hrefs = []
for h3 in soup.fetch('h3'): 
	hrefs.append(h3.a['href'])

posts = []
for post_href in hrefs:
	print 'fetching ' + post_href
	html = urllib.urlopen(post_href).read()
	soup = BeautifulSoup(html)
	for meta in soup.fetch('meta'):
		if meta.get('name') and meta['name'] == 'DC.Date.MODIFIED':
			date = meta['content']
	title = soup.title.string
	epoch = int(time.mktime(time.strptime(date,'%Y-%m-%d')))
	entry = str(soup.first('div','entry'))
	posts.append((title, epoch, entry))

fo = open('posts.marshal','wb')
fo.write(marshal.dumps(posts))
fo.close()