# create reuters.db in format expected by dolphy for simple indexing

# TODO: glob over full reuters collection

import re, glob
import marshal

file = 'reuters/reut2-002.sgm'

news_data = open(file).read()
story_re = re.compile('<REUTERS(.*?)</REUTERS>',re.DOTALL)
body_re = re.compile('<BODY>(.*?)&#3;</BODY>',re.DOTALL)
title_re = re.compile('<TITLE>(.*?)</TITLE>',re.DOTALL)
title_strip = re.compile('&lt;[A-Z\s]+>')

stories = story_re.findall(news_data)

story_count = 0
posts = []

for story in stories:
	try:
		body = body_re.findall(story)[0]
		title = title_re.findall(story)[0]
		title = title_strip.sub('', title).strip()
		if len(title):
			print title
			posts.append((title, body))
			story_count = story_count + 1
	except:
		pass
		
fo = open('reuters.db','w')
fo.write(marshal.dumps(posts))
fo.close()
		
print "added %s stories" % story_count
