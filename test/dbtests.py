# test performance of serialisers and persisted hashes for dolphy
# TODO: try shelve (should be same as dbhash and cPickle)
# TODO: try low level bsdbb driver
# TODO: use more realistic hash
# TODO: compare index filesizes

import dbhash
import time
import marshal
import cPickle as pickle

DBFILE = 'test.db'
REPITITIONS = 1000

db = dbhash.open(DBFILE, flag='c')

print "=== Starting Test with %s repititions ===" % REPITITIONS
# using eval
d = "{'a':['one','two','three'],'b':[3,2,1], 'c':['this is a longer string']}"

start = time.time()

for i in range(0,REPITITIONS):
	db[str(i)] = d
	
print "populated REPITITIONS dicts as strings in %.3f seconds" % (time.time() - start)

start = time.time()

for i in range(0,REPITITIONS):
	out = eval(db[str(i)])['b'][1]
	
print "evaled REPITITIONS dicts as strings in %.3f seconds" % (time.time() - start)

# using marshal

d = {'a':['one','two','three'],'b':[3,2,1], 'c':['this is a longer string']}
start = time.time()

for i in range(0,REPITITIONS):
	db[str(i)] = marshal.dumps(d)
	
print "populated REPITITIONS marshaled dicts in %.3f seconds" % (time.time() - start)

start = time.time()

for i in range(0,REPITITIONS):
	out = marshal.loads(db[str(i)])['c'][0]
	
print "unmarhsaled REPITITIONS dicts in %.3f seconds" % (time.time() - start)

# using pickle

d = {'a':['one','two','three'],'b':[3,2,1], 'c':['this is a longer string']}
start = time.time()

for i in range(0,REPITITIONS):
	db[str(i)] = pickle.dumps(d)
	
print "populated REPITITIONS pickled dicts in %.3f seconds" % (time.time() - start)

start = time.time()

for i in range(0,REPITITIONS):
	out = pickle.loads(db[str(i)])['c'][0]
	
print "unpickled REPITITIONS dicts in %.3f seconds" % (time.time() - start)

start = time.time()

for i in range(0,REPITITIONS):
	out = db[str(i)]
	
print "just fetched all REPITITIONS keys from dbhash in %.3f seconds" % (time.time() - start)