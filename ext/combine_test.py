from sets import Set

class Search:

	def combineMatches(self, doc_groups, join_type="intersection"):
		"""	Combine sets of matching documents, e.g. for each term
			in a multi-term query. Supports intersections (for AND
			queries) and unions (for ORs). """
		# TODO: less frequent terms (across all documents) should
		# be weighted - perhaps this is where to apply the weighting
		combined_set = {}
		doc_groups_copy = list(doc_groups)
		intersected = Set(doc_groups_copy.pop().keys())
		if join_type == "intersection":
			for doc_group in doc_groups_copy:
				intersected = intersected.intersection(Set(doc_group.keys()))
			for doc in intersected:
				positions = []
				len = 0
				for doc_group in doc_groups:
					positions.extend(doc_group[doc][0])
					len = doc_group[doc][1]
				combined_set[doc] = (positions, len)
		elif join_type == "union":
			for doc_group in doc_groups_copy:
				intersected = intersected.union(Set(doc_group.keys()))
			for doc in intersected:
				positions = []
				len = 0
				for doc_group in doc_groups:
					if doc in doc_group:
						positions.extend(doc_group[doc][0])
						len = doc_group[doc][1]
				combined_set[doc] = (positions, len)
		return combined_set

# run the tests
docs_matching_term_1 = {1: ([1,2], 5), 2: ([3,5], 8), 4: ([1,3], 7)}
docs_matching_term_2 = {1: ([4,5], 5), 2: ([4,6], 8), 3: ([6,7], 9), 4: ([2], 7)}
matching_docs = [docs_matching_term_1, docs_matching_term_2]

s = Search()
merged_matches = s.combineMatches(matching_docs, "union")
print merged_matches