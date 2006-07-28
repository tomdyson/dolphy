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