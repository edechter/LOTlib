"""
	class to test Grammar.py
	follows the standards in https://docs.python.org/2/library/unittest.html
"""


import unittest

from LOTlib.Grammar import *
from LOTlib.Proposals.RegenerationProposal import RegenerationProposal
from LOTlib import lot_iter
import math
from collections import defaultdict
from scipy.stats import chisquare



class GrammarTest(unittest.TestCase):


	# initialization that happens before each test is carried out
	def setUp(self):
		pass # We will use a different grammar for each test
		# self.G = Grammar()
		# self.G.add_rule('START', 'A ', ['START'], 0.1)
		# self.G.add_rule('START', 'B ', ['START'], 0.3)
		# self.G.add_rule('START', 'NULL', None, 0.6)

	# tests that the generation and regeneration of trees is consistent with the probabilities
	# that are output by lp_regenerate_propose_to
	def test_lp_regenerate_propose_to(self):
		self.G = Grammar()
		# NOTE: these probabilities should get normalized automatically
		self.G.add_rule('START', 'S', ['NP', 'VP'], 0.1)
		self.G.add_rule('START', 'S', ['INTERJECTION'], 0.3)
		self.G.add_rule('NP', 'NV', ['DET', 'N'], 0.6)
		self.G.add_rule('NP', 'NV', ['DET', 'ADJ', 'N'], 0.4)
		self.G.add_rule('NP', 'NV', ['PN'], 0.3)
		self.G.add_rule('VP', 'NV', ['V', 'NP'], 0.5)
		self.G.add_rule('N', 'ball', None, 0.2)
		self.G.add_rule('N', 'computer', None, 0.2)
		self.G.add_rule('N', 'phone', None, 0.2)
		self.G.add_rule('PN', 'Chomsky', None, 0.3)
		self.G.add_rule('PN', 'Samay', None, 0.3)
		self.G.add_rule('PN', 'Steve', None, 0.3)
		self.G.add_rule('PN', 'Hassler', None, 0.3)
		self.G.add_rule('V', 'eats', None, 0.25)
		self.G.add_rule('V', 'kills', None, 0.25)
		self.G.add_rule('V', 'maims', None, 0.25)
		self.G.add_rule('V', 'sees', None, 0.25)
		self.G.add_rule('ADJ', 'peculiar', None, 0.4)
		self.G.add_rule('ADJ', 'strange', None, 0.4)
		self.G.add_rule('ADJ', 'red', None, 0.4)
		self.G.add_rule('ADJ', 'queasy', None, 0.4)
		self.G.add_rule('ADJ', 'happy', None, 0.4)
		self.G.add_rule('DET', 'the', None, 0.5)
		self.G.add_rule('DET', 'a', None, 0.5)
		self.G.add_rule('INTERJECTION', 'sh*t', None, 0.6)
		self.G.add_rule('INTERJECTION', 'fu*k pi', None, 0.6)
		# the RegenerationProposal class
		rp = RegenerationProposal(self.G)
		numTests = 100
		# Sample 1000 trees from the grammar, and run a chi-squared test for each of them
		for i in lot_iter(range(numTests)):
			# keep track of expected and actual counts
			# expected_counts = defaultdict(int) # a dictionary whose keys are trees and values are the expected number of times we should be proposing to this tree
			actual_counts = defaultdict(int) # same as expected_counts, but stores the actual number of times we proposed to a given tree
			tree = self.G.generate('START')
			
			# Regenerate some number of trees at random
			numTrees = 1000
			for i in range(numTrees):
				newtree = rp.propose_tree(tree)[0]
				# trees.append(newtree)
				actual_counts[newtree] += 1
			# see if the frequency with which each category of trees is generated matches the
			# expected counts using a chi-squared test
			chisquared, p = self.get_pvalue(tree, actual_counts, numTrees)
			print chisquared, p
			# if p > 0.01/1000, test passes
			self.assertTrue(p > 0.01/numTests, "Trees are not being generated according to the expected log probabilities")
	
	# computes a p-value for regeneration, given the expected and actual counts.
	# First groups trees according to probability, then computes the chi-squared statistic, then gets the p-value
	def get_pvalue(self, tree, actual_counts, numTrees):
		# compute a list of expected counts
		expected_counts = defaultdict(int)
		# and keep track of the sum of all probabilities for trees we've seen
		prob_sum = 0
		# now that we've generated all trees, compute the expected number of times we should have proposed
		# to each tree that we've proposed to
		# NOTE: groups trees that are of low probability
		grouped_count = 0 # a variable for storing the counts for trees of very low probability
		for newtree in actual_counts.keys():
			prob = math.exp(self.G.lp_regenerate_propose_to(tree, newtree))
			if prob < 1.0/(1*numTrees):
				grouped_count += actual_counts[newtree]
				del actual_counts[newtree]
				# print "deleted tree", newtree
			else: 
				prob_sum += prob
				expected_counts[newtree] = prob * numTrees
		# the probabilities should sum to less than 1
		self.assertTrue(prob_sum < 1, "Probabilities don't sum to less than 1! " + str(prob_sum))
		# add the "rest of the trees"
		expected_counts[None] = (1 - prob_sum) * numTrees
		actual_counts[None] = grouped_count
		# transform the expected and actual counts dictionaries into arrays
		assert sorted(expected_counts.keys()) == sorted(actual_counts.keys()), "Keys don't match"

		# for t in sorted(expected_counts.keys(), key=lambda x: expected_counts[x]):
		# 	print expected_counts[t], actual_counts[t], t

		expected_values, actual_values = [], []
		for newtree in actual_counts.keys():
			expected_values.append(expected_counts[newtree])
			actual_values.append(actual_counts[newtree])
		# print expected_values, actual_values
		# get the p-value
		return chisquare(np.array(actual_values), f_exp=np.array(expected_values))

	# tests .log_probability() function, without bound variables in the grammar
	# Uses the Grammars/FiniteWithoutBVs.py grammar
	def test_log_probability_FiniteWithoutBVs(self):
		# import the grammar
		from LOTlibTest.Grammars import FiniteWithoutBVs
		self.G = FiniteWithoutBVs.g
		# sample from G 100 times
		for i in range(100):
			t = self.G.generate('START')
			# count probability manually
			prob = FiniteWithoutBVs.log_probability(t)
			# print t, prob, t.log_probability(), prob - t.log_probability()
			# check that it's equal to .log_probability()
			self.assertTrue(math.fabs(prob - t.log_probability()) < 0.00000001)

	# tests .log_probability() function, with bound variables in the grammar
	# Uses the Grammars/FiniteWithoutBVs.py grammar
	def test_log_probability_FiniteWithBVs(self):
		# import the grammar
		from LOTlibTest.Grammars import FiniteWithBVs
		self.G = FiniteWithBVs.g
		# sample from G 100 times
		for i in range(100):
			t = self.G.generate('START')
			# count probability manually
			prob = FiniteWithBVs.log_probability(t)
			print t, prob, t.log_probability(), prob - t.log_probability()
			# check that it's equal to .log_probability()
			self.assertTrue(math.fabs(prob - t.log_probability()) < 0.00000001)

	# manually checks the log probability of a tree produced from the FiniteWithBVs testing grammar
	def log_probability_FiniteWithBVs(self, tree):
		# every tree has an equal probability of being generated
		return math.log(0.5*0.5*(1.0/3)*0.5*0.5)

	# # tests .log_probability() function, without bound variables in the grammar
	# # Uses the Grammars/FiniteWithoutBVs.py grammar
	# def test_log_probability_FiniteWithoutBvArgs(self):
	# 	# import the grammar
	# 	from LOTlibTest.Grammars import FiniteWithoutBvArgs
	# 	self.G = FiniteWithoutBvArgs.g
	# 	# sample from G 100 times
	# 	for i in range(100):
	# 		t = self.G.generate('START')
	# 		# count probability manually
	# 		prob = self.log_probability_FiniteWithoutBvArgs(t)
	# 		print t, prob, t.log_probability(), prob - t.log_probability()
	# 		# check that it's equal to .log_probability()
	# 		self.assertTrue(math.fabs(prob - t.log_probability()) < 0.00000001)

	# # manually checks the log probability of a tree produced from the FiniteWithoutBvArgs testing grammar
	# def log_probability_FiniteWithoutBvArgs(self, tree):
	# 	# every tree has an equal probability of being generated
	# 	return math.log(0.5*0.5*(1.0/3)*0.5*0.5)


	# counts the probability of the grammar manually
	# NOTE: not modular at this point, if we change our test grammar this function will return something incorrect
	# NOTE: also only works if START -> any characters not in NULL (fix)
	def countProbability(self, node):
		# count number of occurrences of A and B
		ls = node.as_list()
		# recursively go through the tree, counting up the number of a's and b's
		counts = self.count(ls)
		# print ls, counts
		return math.log(0.1**counts['A '] * 0.3**counts['B '] * 0.6)


	# counts the number of occurrences of each element in a nested list of strings
	# returns a dictionary
	def count(self, ls):
		# http://stackoverflow.com/questions/9358983/python-dictionary-and-default-values
		dictionary = defaultdict(int)
		# recursively flatten the list
		flattenedList = self.flatten(ls)
		# count the elements one-by-one
		for elem in flattenedList:
			dictionary[elem] += 1
		# return the dictionary
		return dictionary

	# flattens a nested list
	def flatten(self, ls):
		newlist = []
		for elem in ls:
			if type(elem) == list:
				newlist.extend(self.flatten(elem))
			else: newlist.append(elem)
		return newlist














# main code to run the test
if __name__ == '__main__':
	unittest.main()
