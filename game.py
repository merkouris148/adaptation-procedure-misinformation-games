#####################################################################
# class NormalFormGame
# --------------------------------------------------------
# This file includes the class NormalFormGame, which
# encodes a n-player normal form game.
#
# Example:
#	Generate random game
#	| import game
#	|
#	| id = "game_0"
#	| num_players = 2
#	| stategies = [2, 2]
#	|
#	| NFG = game.NormalFormGame(id, num_players, strategies)
#	|
#	| NFG.generate_strategy_profiles()
#	|
#	| max_utilities = 10
#	| NFG.generate_random_utilities(max_utilities)
#
# Instance of: Dictionary: StrategyProfiles --> UtilityVector, aka
#							(Strategy) -->[Utility]
#
# Data Members:
#	String	game_id
#	Int		num_players
#	[Int]	strategies
#
# Methods:
#	Operations:
#		void get_support()
#		void get_nash_equilibria()
#	
#	Initialize:
#		void generate_random_utilities(Int: max_utility)
#
#	Convert:
#		String: gambit_file_format to_gambit()
#		String: clingo_file_format to_clingo()
#
# author: Merkouris Papamichail
# email: mercoyris@ics.forth.gr
# institute: ICS, FORTH
# last update: 25/10/2022
#####################################################################



####################
# Custom Libraries # 
####################

import gambit 	# gambit.support()
				# this is a custom library for command line calls
				# not the API of gambit for python

import parsers # GambitOutputInterpreter

import auxiliary_functions as ax

####################
# Python Libraries #
####################

import pprint	# pretty print
import random	# generate random utilities
import math		# prod
import time


## 3rd party libraries
from termcolor import colored, cprint


#############
# Constants #
#############


#########
# Class #
#########

class NormalFormGame:
	
	## Initialize Data Members
	game_id		= ""
	num_players	= 0
	strategies	= []
	
	## Utilities
	utilities = dict()
	
	## Nash Equilibria
	nash_equilibria = []
	
	## Support
	support = dict()
	
	## states
	game_id_set						= False
	num_players_set					= False
	strategies_set					= False
	strategy_profiles_generated		= False
	utilities_filled				= False
	nash_equilibria_computed		= False
	support_computed				= False
	
	###############
	# Constructor #
	###############
	def __init__(self, gambit_pac, debugging, domain, game_id = "", num_players = 0, strategies = []):

		# Prelimineries
		self.gambit_pac = gambit_pac
		self.debugging	= debugging
		self.domain		= domain

		## Handle Arguments
		self.set_game_id(game_id)
		self.set_num_players(num_players)
		self.set_strategies(strategies)


		## Initialize support dict: we represent the support of each player as a set
		for player in range(1, self.num_players + 1):
			self.support[player] = set()
		
		
	
	
	#####################
	# Convert to String	#
	#####################
	def export_utilities(self):
		# write game id
		output = "# Game id: " + self.game_id + "\n"
		
		# write the nash equilibria
		output += "# Nash Equilibria: " + str(self.nash_equilibria) + "\n"
		
		for sp in self.utilities.keys():
			for util in self.utilities[sp]:
				output += str(util) + " "
			output += "\n"
		
		return output
	
	
	def str_header(self, c, delim):
		# where c in the comment character, i.e. '#', '%' or '//'
		# and delim is the delimiter between the fields
		
		## Convert the attributes to strings
		# Input arguments
		str_game_id 			= str(self.game_id)
		str_num_players 		= str(self.num_players)
		str_strategies			= str(self.strategies)
		
		
		## Check the class state
		# Strategies Generated
		str_strategies = str(self.strategies)
		
		output = c + " Game Id: "			+ str_game_id 				+ delim\
			+ c + " Number of Players: " 	+ str_num_players 			+ delim\
			+ c + " Strategies: " 			+ str_strategies 			+ delim
		
		
		return output
	
	def str_vline(self, c):
		
		return c * 50 + "\n"
	
	def __str__(self):
		# Utilities Generated
		str_utilities = pprint.pformat(self.utilities)# if self.utilities_generated else "Class Game: Utilities not generated!"
				
		## Aesthetics
		vline = self.str_vline("#")
		
		## Output
		output = 	vline 						+ \
					self.str_header("#", "\n") 	+ \
					vline 						+ \
					"\n" 						+ \
					str_utilities 				+ \
					"\n"
		
		return output
	
	
	##################
	# initialization #
	##################
	## Set game's id
	def set_game_id(self, game_id):
		assert self.game_id_set == False, "NormalFormGame: game_id already set!"
		assert game_id != "", "NormalFormGame: game_id should not be empty!"
		
		self.game_id = game_id
		
		self.game_id_set = True
	
	## Set the number of players
	def set_num_players(self, num_players):
		assert self.num_players_set == False, "NormalFormGame: num_players already set!"
		assert num_players >= 2, "NormalFormGame: num_players should be >= 2!"
		
		self.num_players = num_players
		
		self.num_players_set = True
	
	## Set the strategies vector
	def set_strategies(self, strategies):
		## Check Prerequirements states
		assert self.strategies_set == False, "NormalFormGame: strategies already set!"
		
		## Check the number of strategies
		assert self.num_players_set == True, "NormalFormGame: num_players should be set before strategies vector!"
		assert len(strategies) == self.num_players, "NormalFormGame: there should be num_players strategies!"
		
		## Check the input strategies vector
		strategies_check = True
		for strategy in strategies:
			if strategy < 1:
				strategies_check = False
				break
		
		assert strategies_check == True, "NormalFormGame: all strategies should be >= 1!"
		
		
		## Set Variable
		self.strategies = strategies.copy()
		
		## Update State
		self.strategies_set = True
	
	
	## Generalized Initialization Method
	# one initialization method to rule them all
	def initialize(self, game_id, num_players, strategies):
		
		self.set_game_id(game_id)
		self.set_num_players(num_players)
		self.set_strategies(strategies)
		self.generate_strategy_profiles()
	
	
	#####################
	# Strategy Profiles #
	#####################
	#
	# The way this while-loop is constructed is a bit clunky,
	# but I could find a more clean solution.
	# The bound of the while-loop is the last_strategy_profile
	# which is strategy_profile - 1 aka base - 1. This is because
	# of the way the function succ is written. That's way we should
	# do one last iteration.
	#
	def generate_strategy_profiles(self):
		## check prerequirements states
		assert self.strategies_set == True, "NormalFormGame: strategies vector should be set, to generate strategy profiles!"
		assert self.strategy_profiles_generated == False, "NormalFormGames: strategy_profiles already generated!"


		first_sp 	= [0] * self.num_players
		last_sp		= ax.subtract(self.strategies, [1] * self.num_players)
		base		= self.strategies
		strategy_profiles = ax.enumerate_vecs(first_sp, last_sp, base, tuple)


		dummy_utilities = [0] * self.num_players
		self.utilities = {sp : dummy_utilities.copy() for sp in strategy_profiles}

		
		## Update State
		self.strategy_profiles_generated = True
	
	
	######################
	# Generate Utilities #
	######################
	

	def generate_random_utilities(self, max_utility):
		assert self.strategy_profiles_generated == True, "NormalFormGame: strategy profiles should be generated before filing utilities!"
		assert self.utilities_filled == False, "NormalFormGame: utilities already filled!"
		
		## fill existing strategy profiles
		for strategy_profile, utilities in self.utilities.items():
			
			## compute a random utilities vector
			new_utilities = [0 for i in range(self.num_players)]
			for player in range(self.num_players):
				new_utilities[player] = random.randint(0, max_utility)
			
			## update utilities
			self.utilities.update({strategy_profile : new_utilities})
		
		## update state
		self.utilities_filled = True
	
	
	
	#########################################################################
	# See also: MisinformationGame::_answer_set_to_utilities_info_list()
	# & MisinformationGame::utilities_from_clingo()
	#
	# ----------------------------------------------------------------------
	#
	# Input: a list of list of the form [[Game, Player, (Int), Util]]
	# where (Int) encodes a strategy profile as a tuple
	#
	# Action: initialize the utilities from this utility info list.
	#########################################################################
	def utilities_from_list(self, util_info_list):
		assert self.strategy_profiles_generated == True, "NormalFormGame: strategy profiles should be generated before filing utilities!"
		assert self.utilities_filled == False, "NormalFormGame: utilities already filled!"

		
		for util_info in util_info_list:
			(self.utilities[util_info[1]])[util_info[0]-1] = util_info[2]


		## update state
		self.utilities_filled = True
	
	
	# Input: a list of strings, describing the utilities
	# of each player, separated by space " "
	def utilities_from_str(self, lines):
		
		## some preconditions checks
		assert self.strategy_profiles_generated == True, "NormalFormGame: strategy profiles should be generated before filing utilities!"
		assert self.utilities_filled == False, "NormalFormGame: utilities already filled!"
		
		num_SPs = math.prod(self.strategies)
		assert len(lines) == num_SPs
		
		
		for strategy_profiles in self.utilities.keys():
			line = ax.head(lines)
			line = line.split(" ")
			line = list(filter(lambda token: token != "", line))	# Discard empty tokens.
			int_line = list(map(int, line))
			
			self.utilities[strategy_profiles] = int_line
		
		
		## update state
		self.utilities_filled = True
	
	
	##############
	# Predicates #
	##############
	def is_strategy_profile(self, strategy_profile):
		
		return tuple([0] * self.num_players) <= strategy_profile and\
				strategy_profile < tuple(self.strategies)
	
	
	def is_player(self, player):
		
		return 0 <= player and player < self.num_players
	
	
	###########
	# Support #
	###########
	
	# In order to compute the support, we utilize
	# the gambit shell command gambit-pol to get
	# the NE.
	def compute_nash_equilibria(self):
        ## Preconditions
		assert self.utilities_filled == True
		assert self.nash_equilibria_computed == False
		
		
		# GAMBIT call
		gambit_start_t = time.time()
		gambit_out = self.gambit_pac.compute_nash_equilibria(self.gambit_str_file())
		gambit_end_t = time.time()

		# Update the time consumed in GAMBIT
		self.debugging.gambit_call(gambit_end_t - gambit_start_t)

		# Parse GAMBIT's output
		# Use the SPDomain instance in order to rectify GAMBIT's output (if needed)
		# in order to avoid rounding errors.
		if gambit_out != None:
			self.nash_equilibria = parsers.parse_gambit_out_file(self.num_players, self.strategies, gambit_out)
			self.nash_equilibria = self.domain.default_mapping_list(self.nash_equilibria)

		# Debugging module: Check if GAMBIT's output has errors.
		self.debugging.check_no_nash(self.nash_equilibria)
		self.debugging.check_zeros_mixed_strategy(self.nash_equilibria)
		self.debugging.check_mixed_strat_lt_one(self.nash_equilibria)
        
        
		## Postcondition: update state
		self.nash_equilibria_computed = True


	def compute_support(self):
        ## Preconditions
		assert self.nash_equilibria_computed == True
		assert  self.support_computed == False
        
        
		for nash_equilibrium in self.nash_equilibria:

			for player in range(1, self.num_players + 1):
				for strategy in range(self.strategies[player]):

					if nash_equilibrium[player][strategy] > 0:
						self.support[player].add(strategy + 1)
        
        ## Postcondition
		self.support_computed = True
    
    
	def get_support(self):
		assert self.support_computed == True
		
		return self.support
	
	def get_nash_equilibria(self):
		assert self.nash_equilibria_computed == True
		
		return self.nash_equilibria
	
	####################
	# CLINGO Formating #
	####################
	
	def clingo_str_num_players(self):
		output = "num_players(" + str(self.num_players) + ").\n"
		return output
	
	def __clingo_str_pl_strategies(self, player):
		assert(1 <= player and player <= self.num_players)
		
		output = "s(" + str(player) + ", 1.." + str(self.strategies[player-1]) + ").\n"
		return output
	
	def clingo_str_strategies(self):
		output = ""
		for player in range(1, self.num_players+1):
			output += self.__clingo_str_pl_strategies(player)
		
		return output
	
	def __clingo_str_strategy_profile(self, strategy_profile):
		assert(self.is_strategy_profile(strategy_profile))
		
		output = ""
		for s in strategy_profile:
			output += "sp(" + str(s + 1) + ", "
		
		output += "nul"
		output += ")" * self.num_players
		
		return output
	
	def __clingo_str_sp_pl_utility(self, strategy_profile, player):
		assert self.is_strategy_profile(strategy_profile) and self.is_player(player)
		
		output = "u(" + self.game_id + ", " + str(player + 1) + ", "
		output += self.__clingo_str_strategy_profile(strategy_profile)
		output += ", "
		
		u = self.utilities[strategy_profile][player]
		
		output += str(u) + ")."
		
		return output
	
	def __clingo_str_pl_utility(self, player):
		assert self.is_player(player)
		
		output = ""
		for strategy_profile in self.utilities.keys():
			output += self.__clingo_str_sp_pl_utility(strategy_profile, player)
			output += "\n"
		
		return output
	
	def clingo_str_utility(self):
		output = ""
		
		for player in range(self.num_players):
			output += "\n" * 2
			output += self.__clingo_str_pl_utility(player)
		
		return output

	
	def clingo_str_file(self):
		
		str_file =  self.str_vline("%")
		str_file += self.str_header("%", "\n")
		str_file += self.str_vline("%")				+ "\n"
		str_file += self.clingo_str_utility()		+ "\n"
		
		return str_file
	
	
	####################
	# Gambit Formating #
	####################
	
	def __gambit_str_prologue(self):
		## writing prefix and title
		output = "NFG 1 R"	# standard prefix of .nfg gambit file format
		output += " \"" + self.str_header("", " ") + "\""
		
		## writing players
		output += " { "
		for player in range(self.num_players):
			output += "\"Player " + str(player + 1) + "\" "
		output += "}"
		
		## writing strategies
		output += "{ "
		for player in range(self.num_players):
			output += str(self.strategies[player]) + " "
		output += "}\n"
		
		return output
	
	
	def __gambit_str_body(self):
		
		output = ""
		for strategy_profile in self.utilities.keys():
			utilities = self.utilities[strategy_profile]
			for u in utilities:
				output += str(u) + " "
		
		return output
	
	
	def gambit_str_file(self):
		output = self.__gambit_str_prologue() + self.__gambit_str_body()
		
		return output
