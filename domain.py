#############
# Libraries #
#############

## native libraries
import time

## 3rd party library
import numpy as np

## custom libraries
import auxiliary_functions as ax


class domain_methods_vals:
	voronoi	= 0
	real	= 1

domain_methods_vals_list =[
	domain_methods_vals.voronoi,
	domain_methods_vals.real
]

class domain_method_names:
	voronoi	= "Voronoi"
	real	= "Real"

###########################
# Strategy Profile Domain #
###########################

class SPDomain:
	###############
	# Constructor #
	###############
	def __init__(self, method_val = domain_methods_vals.real):
		assert method_val in domain_methods_vals_list

		self.default_method_val = method_val
		self.num_players 	= -1	# dummy value
		self.strategies 	= []	# dummy value
		self.vector_domains = []	# dummy value

		## States
		self.initialised = False

	def initialise(self, num_players, strategies):
		assert self.initialised == False
		assert num_players >= 0
		assert num_players == len(strategies)

		self.num_players = num_players
		self.strategies = strategies

		## Strategy Profile Domain is just a list of VectorDomain instances
		for player in range(num_players):
			self.vector_domains.append(VectorDomain(strategies[player], self.default_method_val))

		self.initialised = True

	###################
	# Mapping Methods #
	###################
	def real_mapping(self, strategy_profile):
		assert self.initialised == True

		strategy_profile_out = []
		for player in range(self.num_players):
			strategy_out = self.vector_domains[player].real_mapping(strategy_profile[player])
			strategy_profile_out.append(strategy_out)

		return tuple(strategy_profile_out)

	def voronoi_mapping(self, strategy_profile):
		assert self.initialised == True

		strategy_profile_out = []
		for player in range(self.num_players):
			strategy_out = self.vector_domains[player].voronoi_mapping(strategy_profile[player])
			strategy_profile_out.append(strategy_out)

		return tuple(strategy_profile_out)

	def default_mapping(self, strategy_profile):
		assert self.initialised == True

		if self.default_method_val == domain_methods_vals.voronoi:
			return self.voronoi_mapping(strategy_profile)

		if self.default_method_val == domain_methods_vals.real:
			return self.real_mapping(strategy_profile)

	def default_mapping_list(self, strategy_profile_list):
		assert self.initialised == True

		strategy_profile_set = set()
		for SP in strategy_profile_list:
			strategy_profile_set.add(self.default_mapping(SP))

		return list(strategy_profile_set)


#################
# Vector Domain #
#################

class VectorDomain:
	###############
	# Constructor #
	###############
	def __init__(self, dimension, method_val = domain_methods_vals.real):
		assert method_val in domain_methods_vals_list

		## Data Members
		self.dimension				= dimension
		self.voronoi_seeds			= []
		self.num_voronoi_cells		= 2**dimension
		self.default_method_val 	= method_val
		self.default_method_name	= ""

		## Initialize default methods name
		if self.default_method_val == domain_methods_vals.voronoi:
			self.default_method_name = domain_method_names.voronoi

		if self.default_method_val == domain_methods_vals.real:
			self.default_method_name = domain_method_names.real


		## enumerate all possible supports
		first_support_vector		= [0] * self.dimension
		last_support_vector			= [1] * self.dimension
		base						= [2] * self.dimension
		support_vector_enumeration = ax.enumerate_vecs(first_support_vector, last_support_vector, base, np.array)
		#print(support_vector_enumeration)
		## create a vector for each possible support,
		## by taking the "middle" for this support
		for vec in support_vector_enumeration:
			k = ax.count_support(vec)
			if k > 0:									# a somewhat proxeiro patch
				self.voronoi_seeds.append(vec / k)
				#print(vec / k)



	###################
	# Mapping Methods #
	###################
	## Real Mapping: x |--> x
	def real_mapping(self, vector):
		assert len(vector) == self.dimension
		return vector


	## Voronoi Mapping: x |--> s,
	## where s is the seed of the Voronoi cell,
	## where x belongs to
	def voronoi_mapping(self, vector):
		assert  len(vector) == self.dimension


		np_vector = np.array(vector)
		pos			= 0
		min_dist	= np.inf
		for i in range(len(self.voronoi_seeds)):
			dist = np.linalg.norm(self.voronoi_seeds[i] - np_vector)
			if dist < min_dist:
				min_dist	= dist
				pos			= i

		return tuple(self.voronoi_seeds[pos])


	def default_method(self, vector):

		if self.default_method_val == domain_methods_vals.voronoi:
			return self.voronoi_mapping(vector)

		if self.default_method_val == domain_methods_vals.real:
			return self.real_mapping(vector)


