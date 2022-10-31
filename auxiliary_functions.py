#####################################################################
# auxiliary_functions.py
# ------------------------------------------------------------------
# Some auxiliary functions that are used from the other classes.
#
# Functions:
#
#	1)	simple_list2str: [str] --> str
#			Concatenates all the strings from a list of strings, to
#			a simple string.
#
#	2) head: [t] --> t
#		Returns the first element of a list and removes it from the
#		list.
#
#	3) subtract: [int], [int] --> [int]
#		Takes two vectors encoded as list, e.g. v1, v2 and returns
#		their difference, i.e. v1 - v2.
#
#	4) succ: [int], int, int --> [int]
#		Returns the successor of a number in a specific system. I.e.
#		returns (x + 1)_b, if the number x is passed as a list of
#		digits in the b-based arithmetic system. The 3rd parameter is
#		used as curry from the function.
#
#		Example:
#			succ([0, 0, 1], 2, 0) --> [0, 1, 0]
#
#	5) path_to_set: [t] --> (t)
#		Given some sequence of of elements as a list, sorts the
#		elements and deletes the duplicates. The result is a tuple.
#
#		Example:
#			path_to_set([3, 2, 2, 1, 3]) --> (1, 2, 3) 
#
# author: Merkouris Papamichail
# email: mercoyris@ics.forth.gr
# institute: ICS, FORTH
# last update: 13/4/2022
#####################################################################

##################
# List Functions #
##################

## Conversions
def simple_list2str(str_list):
	output = ""
	for s in str_list:	output += s
	
	return output



## List operations
def head(l):
	return l.pop(0)



## Vector Operations
def subtract(vector1, vector2):
	assert(len(vector1) == len(vector2))
	
	d = len(vector1)
	difference = [0] * d
	for i in range(d):
		difference[i] = vector1[i] - vector2[i]
	
	return difference

def add(vec1, vec2):
	assert (len(vec1) == len(vec2))

	d = len(vec1)
	summary = [0] * d
	for i in range(d):
		summary[i] = vec1[i] + vec2[i]

	return summary

## Counting
#
# Returns the successor of a given vector.
# A variant of binary counting.
#
# Given a vector v and a "base" vector
# b, this function adds + 1 to the *first* cell
# of v s.t. (v + 1) < b
#
# E.g.: [1, 1], [2, 1], [1, 2], [2, 2]
# we inherited this "inverse" counting by the GAMIT's
# input format.
# (See: https://gambitproject.readthedocs.io/en/latest/formats.html#structure-of-the-body-list-of-payoffs)
def succ(vector, base, curry):
	assert vector != [] or curry == 0, "auxiliary_functions.py: succ: Overflow!"
	
	if vector == []: return []
	
	v = head(vector)
	b = head(base)
	
	if curry == 0:	return [v]		+ vector
	if v + 1 < b:	return [v+1] 	+ succ(vector, base, 0)
	else:			return [0]		+ succ(vector, base, 1)


def enumerate_vecs(first_vec, last_vec, base_vec, convert = lambda x : x,step = 1):
	dim = len(first_vec)
	assert len(last_vec) == dim and len(base_vec) == dim

	enumeration = []
	current_vec	= first_vec.copy()

	enumeration.append(convert(current_vec))

	while current_vec < last_vec:
		current_vec = succ(current_vec.copy(), base_vec.copy(), step)
		enumeration.append(convert(current_vec))

	return enumeration


def count_support(vec):
	return len(list(filter(lambda vec_i: vec_i > 0, vec)))		# pythonisms..


def support_indices(vec):
	return [i for i, x in enumerate(vec) if x > 0]				# pythonisms everywhere!


def complete_zeros(vec, length):
	assert len(vec) <= length

	vec_out = [0] * length
	for i in range(len(vec)):
		vec_out[i] = vec[i]

	return vec_out


def _is_prime(primes, p):

	for n in primes:
		if p % n == 0:
			return False

	return True

def n_primes(N):
	assert N >= 0

	primes = [2]
	current_n = 3
	while len(primes) < N:
		if _is_prime(primes, current_n):
			primes.append(current_n)

		current_n += 2

	return primes


## Path to Set
# From a path of the form [v1, v3, v2, v6, v7, v3]
# we create the set (as tuple) (v1, v2, v3, v6, v7),
# i.e. we delete duplicates and sort

###################################################################################################
# NOTE: Python doesn't sort the sets by default,
# See:
#
# StackExchange:
#
# 	https://stackoverflow.com/questions/48615024/why-doesnt-a-set-in-python-have-a-sort-method
#
# From Python Doc:
#
#	https://docs.python.org/3.8/tutorial/datastructures.html#sets
#
#	|
# 	| 	"A set is an *unordered* collection with no duplicate elements."
#	|
#
###################################################################################################
def path_to_set(path):
	
	if path == None:  return ()
	
	tmp = path.copy()
	tmp.sort()
	return  tuple(set(tmp))


##############
# Predicates #
##############


def sp_lt_one(sp):

	for strategy in sp:
		if sum(strategy) < 1:	return True

	return False


def sp_is_zeros(sp):

	for strategy in sp:
		if strategy == tuple([0]*len(strategy)):
			return True

	return False


##########
# CLINGO #
##########

def pos_vec2clingo(pos_vec):
	num_players = len(pos_vec)

	clingo_pos_vec = "pos("
	for strategy in pos_vec:
		clingo_pos_vec += "sp(" + str(strategy) + ", "

	clingo_pos_vec += "nul"
	clingo_pos_vec += ")" * num_players
	clingo_pos_vec += ")."

	return clingo_pos_vec