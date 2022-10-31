
#####################################################################
# class MisinformationGame
# --------------------------------------------------------
#
# This file includes the class MisinformationGame, which
# encodes a n-player misinformation game, i.e. a list of
# n+1 NFGs. NFGs[0] is the "real" game, while the games
# NFGs[1] ... NFGs[n] are the misinformed games of each
# player.
#
# Example:
#	
#	Generate randomly unitilities of a misinformation game
#	| import misinformation_game as mg
#	| 
#	| id = "mg_0"
#	| num_players = 2
#	| strategies = [2, 2]
#	|
#	| MG = mg.MisinformationGame(id, num_players, strategies)
#	|
#	| max_utility = 10
#	| MG.generate_random_utilities(max_utility)
#	|
#	| MG.compute_nme_dict()
#	| MG.compute_pos_vecs()
#	| MG.clingo_compile_format()
#	| MG.clingo_compile_nme()
#
#
# Instance of: List
#
# Data Members:
#	String			game_id
#	Int				num_players
#	[Int]			strategies
#	dict: Players --> Strategies NME
#
# Methods:
#	1. generate_random_utilities(Int: max_utility)
#	2. utilities_from_clingo(String: answer_set)
#	3. compute_nme_dict()
#	4. compute_pos_vecs()
#	5. clingo_compile_format()
#	6. clingo_compile_nme_list()
#
# author: Merkouris Papamichail
# email: mercoyris@ics.forth.gr
# institute: ICS, FORTH
# last update: 25/10/2022
#####################################################################


#############
# Libraries #
#############


## Custom Libraries
import game
import auxiliary_functions as ax


## Python Libraries
import pprint
import re		# regular expressions
import itertools
import threading

## 3rd party libraries
from termcolor import colored, cprint


#########
# Class #
#########


class MisinformationGame:
	
	###############
	# Constructor #
	###############

	def __init__(self, gambit_pac, debugging, domain, game_id, num_players, strategies):
		assert num_players >= 2
		assert len(strategies) == num_players

		# Prelimineries: GAMBIT
		self.gambit_pac = gambit_pac
		# Prelimineries: DEBUGGING
		self.debugging 	= debugging
		# Prelimineries: DOMAIN
		self.domain		= domain

		self.game_id 		= str(game_id)
		self.num_players	= num_players
		self.strategies		= strategies
		
		# Knowledge
		self.total_knowledge		= None
		self.knowledge				= None
		self.knowledge_percentage	= None
		
		## Initialize list of games
		self.games = []
		for player in range(0, self.num_players + 1):
			NFG = game.NormalFormGame(self.gambit_pac, debugging, self.domain, str(player), self.num_players, self.strategies)
			NFG.generate_strategy_profiles()
			self.games.append(NFG)
		
		## Dictionary: NMEs --> PositionVectors
		self.nme = dict()
		
		## The set of SMEs
		# This set will be computed, for each MG
		# during the Adaptation Procedure
		self.sme = set()
		
		## Initialize clingo format
		self.clingo_format = ""
		
		## Dictionary: NMEs --> PositionVectors
		self.nme_clingo = dict()	# this will be a list of strings
									# of the form
									# ["pos(<SP1>).", "pos(<SP2>).", .., "pos(<SPm>)."]
		
		## states
		self.utilities_generated 		= False
		self.nme_computed				= False
		self.pos_vecs_computed			= False
		self.clingo_format_compiled		= False
		self.nmes_clingo_compiled		= False
		self.knowledge_computed			= False
	
	#############
	# Accessors	#
	#############
	
	def initialization_completed(self):
		return 	self.utilities_generated	== True 	and\
				self.nme_computed			== True		and\
				self.pos_vecs_computed 		== True		and\
				self.clingo_format_compiled	== True		and\
				self.nmes_clingo_compiled 	== True		#and\
				#self.knowledge_computed 	== True
	
	def get_knowledge_percentage(self):
		return self.knowledge_percentage
	
	def get_num_nmes(self):
		assert self.initialization_completed()
		assert len(self.nme_clingo) == len(self.nme)
		
		return len(self.nme.keys())
	
	def get_nme_dict(self):
		assert self.initialization_completed()
		assert len(self.nme_clingo) == len(self.nme)
		
		return self.nme
	
	def get_nme_list(self):
		assert self.initialization_completed()
		assert len(self.nme_clingo) == len(self.nme)
		
		return self.nme.keys()
	
	def get_position_vectors(self):
		assert self.initialization_completed()
		assert len(self.nme_clingo) == len(self.nme)
		
		return self.nme.values()
	
	def get_smes(self):
		return self.sme
	
	def get_nme_clingo(self):
		assert self.initialization_completed()
		assert len(self.nme_clingo) == len(self.nme)
	
		return self.nme_clingo
	
	def get_game_id(self):
		return self.game_id
	
	def get_num_players(self):
		return self.num_players
	
	def get_strategies(self):
		return self.strategies
	
	def get_clingo_format(self):
		assert self.clingo_format_compiled == True
		
		return self.clingo_format
	
	def get_clingo_nme_dict(self):
		assert self.nmes_clingo_compiled == True
		
		return self.nme_clingo
	
	
	#############
	# Modifiers #
	#############
	
	def insert_sme(self, sme):
		self.sme.add(sme)
	
	
	#####################
	# Convert to String	#
	#####################
	
	def export(self):
		output = "# Misinformation Game: " + self.get_game_id() + "\n"
		output += "# Knowledge Percentage: " + str(self.knowledge_percentage) + "%\n"
		output += "# NMEs: " + str(self.get_nme_list()) + "\n"
		output += "# SMEs: " + str(self.get_smes()) + "\n"
		
		# Write the number of players
		output += "# num players\n"
		output += str(self.get_num_players())
		output += "\n\n"
		
		# Write strategies
		output += "# strategies\n"
		for strat in self.get_strategies():
			output += str(strat) + " "
		output += "\n\n"
		
		# Write the games
		for i in range(0, self.get_num_players() + 1):
			#output += "# game " + str(i) + " utilities\n"
			output += self.games[i].export_utilities()
			output += "\n\n"
		
		return output
	
	def __str__(self):
		
		## print NMEs
		str_out = "| MG id: " + str(self.game_id) + "\n"
		str_out += "| Knowledge Percentage: " + str(self.knowledge_percentage) + "%\n"
		str_out += "| NMEs list: " + str(self.get_nme_list()) + "\n"
		str_out += "| Posistion Vectors: " + str(self.get_position_vectors()) + "\n"
		str_out += "| SMEs: " + str(self.get_smes())
		
		return str_out
	
	
	######################
	# Generate Utilities #
	######################
	
	def generate_random_utilities(self, max_utility):
		assert self.utilities_generated == False
		
		for player in range(0, self.num_players + 1):
			self.games[player].generate_random_utilities(max_utility)
		
		## update state
		self.utilities_generated = True
	
	
	## Utilities from Clingo
	def _SP_string_to_tuple(self, clingo_sp_string):
		
		# remove th "sp" prefix
		sp_str = re.sub("sp", "", clingo_sp_string)
		
		# remove the "nul" token
		sp_str = re.sub("nul", "", sp_str)
		
		# remove parenthesis
		sp_str = re.sub("\(", "", sp_str)
		sp_str = re.sub("\)", "", sp_str)
		
		# tokenize
		sp_str_list = sp_str.split("-")
		
		# remove the empty tokens, if any
		while "" in sp_str_list:
			sp_str_list.remove("")
		
		sp_int_list = map(lambda strategy : int(strategy) - 1 , sp_str_list)
		
		## return a tuple
		return tuple(sp_int_list)
		
	
	# This function is a *mutator* and it is *automatically* called when the
	# utilities are generated form the CLINGO answer set, i.e. the
	# utilities_from_clingo() method is invoked.
	#
	# Thus, we compute the agents' social (total) knowledge in this
	# misinformation game.
	def compute_knowledge_from_answer_set(self, answer_set):
		## tokenize the answer set
		# split the tokens by space " ".
		tokens = answer_set.split(" ")
		
		# discard the empty tokens, if any
		tokens = list(filter(lambda token: token != "", tokens))
		
		
		knowledge_predicate = "new_frac_knowledge\(.*\)"
		knowledge_token = None
		for token in tokens:
			if re.search(knowledge_predicate, token) != None:
				knowledge_token = token
				break
		
		knowledge_token = re.sub("new_frac_knowledge\(", "", knowledge_token)
		knowledge_token = re.sub("\)", "", knowledge_token)
		knowledge_token = knowledge_token.split(",")
		self.knowledge = int(knowledge_token[0])
		self.total_knowledge = int(knowledge_token[1])
		self.knowledge_percentage = round((self.knowledge / self.total_knowledge) * 100, 2)
		
		self.knowledge_computed = True
	
	
	
	##########################################################
	# Input: 	The "raw" answer set as given by clingo, as 
	#			string of predicates.
	#
	# Output:	The processed AS as list of lists of the form
	#			[[Game, Player, StrategyProfile, Utility]]
	#			Types [[Int, Int, (Int), Int]]
	##########################################################
	def _answer_set_to_utilities_info_list(self, answer_set):
		## determine the knowledge
		self.compute_knowledge_from_answer_set(answer_set)
		
		## tokenize the answer set
		# split the tokens by space " ".
		tokens = answer_set.split(" ")
		
		# discard the empty tokens, if any
		tokens = list(filter(lambda token: token != "", tokens))
		
		
		# a regular expression (roughly) describing a utility
		# predicate
		utilities_predicate = "v\(.*\)"
		
		
		## remove other predicates, if any
		other_predicates = []
		for token in tokens:
			if re.search(utilities_predicate, token) == None:
				other_predicates.append(token)
		for remove_token in other_predicates:
			tokens.remove(remove_token)

		
		## remove the prefix "v" and keep the relation
		tokens = list(map(lambda token: re.sub("v", "", token), tokens))
		
		
		## remove parenthesis
		tokens = list(map(lambda token: re.sub("^\(", "", token), tokens))
		tokens = list(map(lambda token: re.sub("\)$", "", token), tokens))
		
		## change the entries splitting commas ',' to dashes '-',
		# while maintaining the commas in strategy profiles
		tokens = list(map(lambda token: re.sub("sp\(([0-9]+),", r"sp(\1-", token), tokens))

		
		## get the utilities as list of lists
		# this list of list will be of the form
		# [["Game", "Player", "SP", "Util"]]
		utilities_list = list(map(lambda token: token.split(","), tokens))

		## getting from list of lists of string to a int and
		# int tuple list of list.
		# given the list [["Game", "Player", "SP", "Util"]]
		# we want to get [[Game, Player, (Int), Util]]
		# for the entries Game, Player, Util the conversion is
		# straight forward, for the strategy profile, we have to
		# utilize some more elaborate method!
		
		# we define (again roughly) a regular expression
		# for the strategy profile. Remember, we represent
		# the strategy profiles in clingo with a list, e.g.
		# sp(1, sp(2, sp(3, nul)))
		# is representing the strategy profile (1, 2, 3).
		sp_regex = "sp\(.*\)"
		
		utilities_info = []
		for util in utilities_list:
			util_info = []
			for entry in util:
				# easy conversion from string to int
				if re.search(sp_regex, entry) == None:
					util_info.append(int(entry))
				# strategy profile entry, a little more
				# work is needed to convert to (Int)
				else:
					util_info.append(self._SP_string_to_tuple(entry))
			
			utilities_info.append(util_info)
		
		## return list of lists
		return utilities_info
	
	
	def utilities_from_clingo(self, answer_set):
		assert self.utilities_generated == False
		
		utilities_info = self._answer_set_to_utilities_info_list(answer_set)
		
		# create Dict:Player's Game --> Utilities Info
		game_info = dict()
		for player in range(0, self.num_players+1):
			game_info[player] = []
		
		for util_info in utilities_info:
			game = ax.head(util_info)
			game_info[game].append(util_info)

		
		
		for game in range(0, self.num_players + 1):
			self.games[game].utilities_from_list(game_info[game])
		
		
		## update state
		self.utilities_generated = True
	
	
	##################################
	# Natural Misinformed Equilibria #
	##################################


	def _compute_nash_equilibria(self, player):
		assert 0 <= player and player <= self.num_players

		self.games[player].compute_nash_equilibria()


	# Computing the nme dictionary, i.e.
	# 	Dict: Player --> Strategies
	# Note that the method nfg.compute_support()
	# computes also the Nash equilibria.
	def compute_nme_dict(self):
		assert self.nme_computed == False


		for i in range(self.num_players + 1):
			self.games[i].compute_nash_equilibria()


		# a Dict:Players -->[mixed strategies]
		strategies = dict()
		for player in range(1, self.num_players + 1):
			strategies[player] = []
		
		for player in range(1, self.num_players + 1):

			nash_equilibria = self.games[player].get_nash_equilibria()
			
			for NE in nash_equilibria:
				strategies[player].append(NE[player-1])
			
		# compute the NMEs as Cartessian Product of NEs
		for nme in itertools.product(*strategies.values()):
			self.nme[nme] = []
		
		## update state
		self.nme_computed = True
	
	
	
	################################################
	# Compute the cartessian product
	# 	Precondition: nme dictionary computed
	#
	# Computing a list of position vectors,
	# i.e.
	#	[(s_{1, 1}, s_{2, 1}, ..., s_{n, 1}),
	#	(s_{1, 2}, s_{2, 2}, ..., s_{n, 2}),
	#	...
	#	(s_{1, k_1}, s_{2, k_2}, ..., s_{n, k_n})]
	#
	# where s_{m, i} is a support strategy
	# of player m. We computed the support
	# with compute_nme_dict()
	################################################
	def compute_pos_vecs(self):
		assert self.nme_computed == True
		assert self.pos_vecs_computed == False
	
		for nme in self.nme.keys():
			
			# Dict: Players --> position of support
			positions = dict()
			for player in range(1, self.num_players + 1):
				# some pythonism
				positions[player] = [ind + 1 for ind in range(len(nme[player-1])) if nme[player-1][ind] > 0]
			
			# more pythonisms
			for pos_vec in itertools.product(*positions.values()):
				self.nme[nme].append(pos_vec)
			
			
		## update object's state
		self.pos_vecs_computed = True
		
	
	####################
	# CLINGO Formating #
	####################
	
	def clingo_compile_format(self):
		assert self.utilities_generated == True
		assert self.clingo_format_compiled == False
		
		## print number of players
		self.clingo_format += "num_players(" + str(self.num_players) + ").\n"
		
		## print strategies
		for player in range(1, self.num_players + 1):
			self.clingo_format += "s(" + str(player) + ", 1.." + str(self.strategies[player-1]) + ").\n"
		
		## print utilities
		for player in range(0, self.num_players + 1):
			self.clingo_format += self.games[player].clingo_str_file()
		
		# update state
		self.clingo_format_compiled = True
	
	
	def clingo_compile_nme(self):
		assert self.nme_computed == True
		assert self.pos_vecs_computed == True
		assert self.nmes_clingo_compiled == False
		
		## Initialize nme_clingo dictionary
		for nme in self.nme.keys():
			self.nme_clingo[nme] = []
		
		for nme in self.nme.keys():
			for pos_vec in self.nme[nme]:
				
				#clingo_pos_vec = "pos("
				#for strategy in pos_vec:
				#	clingo_pos_vec += "sp(" + str(strategy) + ", "
				#
				#clingo_pos_vec += "nul"
				#clingo_pos_vec += ")" * self.num_players
				#clingo_pos_vec += ")."

				clingo_pos_vec = ax.pos_vec2clingo(pos_vec)

				self.nme_clingo[nme].append(clingo_pos_vec)
			
		# update state
		self.nmes_clingo_compiled = True
