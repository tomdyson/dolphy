#from __future__ import division
import re


whitespace_splitter = re.compile("\\W+", re.U)
query = 'charlie'

def summaryInfo(document, document_length, term_frequency, positions):
	print "\nDocument: " + document
	print "Positions: " + str(positions)
	print "Document length: " + str(document_length)
	print "Term Frequency: " + str(term_frequency)

def algorithm1(document, document_length, term_frequency, positions):
	"""Simple sum over terms of document length divided by position """
	rank = 0.0
	for position in positions:
		rank += (float(document_length)/float(position))
	print document + ": " + str(rank)
	return rank

def algorithm2(document, document_length, term_frequency, positions):
	"""Cumlative sum over terms of document length divided by position"""
	rank = 1.0
	for position in positions:
		rank = rank*(float(document_length)/float(position))
	print document + ": " + str(rank)
	return rank

def algorithm3(document, document_length, term_frequency, positions):
	"""
	Sum over terms of 1/term position. 
	Sum then multiplied by term frequency
	"""
	rank=0.0
	for position in positions:
		rank += (1.0/float(position))
	rank = rank*float(term_frequency)
	print document + ": " + str(rank)
	return rank

def algorithm4(document, document_length, term_frequency, positions):
	"""
	Sum over terms of 1/term position. 
	Sum then multiplied by term frequency squared
	"""
	rank=0.0
	for position in positions:
		rank += (1.0/float(position))
	rank = rank*float(term_frequency**2.0)
	print document + ": " + str(rank)
	return rank

def algorithm5(document, document_length, term_frequency, positions):
	"""
	An attempt to tail off the weighting of term position as one travels 
	further into the document
	
	Sum over terms of (document length (+1) - position) divided by position. 
	Sum is then multiplied by term frequency squared.
	"""

        rank = 0.0
	for position in positions:
	        rank += (float(document_length + 1.0 - position))/float(position)
	rank = rank*float(term_frequency**2.0)
	print document + ": " + str(rank)
	return rank

def algorithm6(document, document_length, term_frequency, positions):
	"""
	Weight posn 1 in the document with a weight of 2 and position
	document_length with a weight of 1 with the weighting of postions
	intermediary to this falling off steeply towards the end of the document.
	Leads to a weighting scheme: 
	weight = (2*(document_length -1))/(x + document_length -2)

	Sum the weights over the terms, 

	Multiply by term_frequency - commented out for now
	"""
	rank = 0.0
	for position in positions:
		rank += (2.0*(float(document_length) -1.0))/(float(position) + float(document_length) -2.0)
	print document + ": " + str(rank)
	return rank
	
def algorithm7(document, document_length, term_frequency, positions):
	"""
	Weight posn 1 in the document with a weight of 2 and position
	document_length with a weight of 1 with the weighting of postions
	intermediary to this falling off steeply towards the end of the document.
	Leads to a weighting scheme: 
	weight = (2*(document_length -1))/(x + document_length -2)

	Sum the weights over the terms, 

	Multiply by term_frequency - commented out for now
	"""
	rank = 0
	for position in positions:
		rank += (2 * (document_length - 1)) / (position + document_length - 2)
	print document + ": " + str(rank)
	return rank
"""
print document information summary
"""
for document in ['doc1.txt', 'doc2.txt', 'doc3.txt']:
	document_contents = open(document).read()
	terms = whitespace_splitter.split(document_contents)
	document_length = len(terms)
	position = 1
	positions = []
	for term in terms:
		if term.lower() == query.lower():
			positions.append(position)
		position += 1
	term_frequency = len(positions)
	summaryInfo(document, document_length, term_frequency, positions)


for algorithm in [algorithm1,algorithm2,algorithm3,algorithm4,algorithm5,algorithm6,algorithm7]:
	print str(algorithm)
	largest_rank = 0.0
	"""ranksarray = zeros([2,3], 'd')"""

	numdoc = -1;
	for document in ['doc1.txt', 'doc2.txt', 'doc3.txt']:
		numdoc += 1
		document_contents = open(document).read()
		terms = whitespace_splitter.split(document_contents)
		document_length = float(len(terms))
		position = 1
		positions = []
		for term in terms:
			if term.lower() == query.lower():
				positions.append(position)
			position += 1
		term_frequency = len(positions)
		rank = algorithm(document, document_length, term_frequency, positions)
		if (rank > largest_rank): 
		        largest_rank = rank
		"""
		ranksarray[0][numdoc] = document
		ranksarray[1][numdoc] = rank
		"""
	"""print ranksarray"""
	
