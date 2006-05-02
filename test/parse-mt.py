import re
import marshal
import time

tb = open('../data/tb.txt').read()
items = tb.split('--------\nAUTHOR:')
title_re = re.compile('TITLE: (.*)')
# DATE: 11/13/2005 11:35:02 PM
date_re = re.compile('DATE: (.*)')
body_re = re.compile('\nBODY:\n(.*?)\n-----\n',re.DOTALL)
ex_body_re = re.compile('\nEXTENDED BODY:\n(.*?)\n-----\n',re.DOTALL)

posts = []

for item in items:
	title = title_re.findall(item)[0]
	print "Title: " + title
	date = date_re.findall(item)[0]
	print "Date: " + date
	epoch = int(time.mktime(time.strptime(date,'%m/%d/%Y %I:%M:%S %p')))
	print "Epoch: " + str(epoch)
	body = body_re.findall(item)[0]
	#print "Body: " + body
	extended = ex_body_re.findall(item)[0]
	#print "Extended: " + extended
	body = body + ' ' + extended
	posts.append((title, body, epoch))
	
fo = open('posts.db','w')
fo.write(marshal.dumps(posts))
fo.close()