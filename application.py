#####################################################################
# application.py
# ------------------------------------------------------------------
# This module handles the command-line, user-defined arguments. A
# calling code file, e.g. the main.py only needs to create an instance
# of the Application function and call the method exec().
#
# Usage Example:
#
#	| import application.py
#	| import sys
#	|
#	| app = application.Application(sys.argv)
#	| app.exec()
#
# For the available user-arguments see the args class.
#
# Classes:
#
#	1) args:			Holds the strings that correspond to the
#						user defined arguments, as data members.
#						Also, provides the methods for determining
#						whether a particular argument is passed by
#						the user to the application. Lastly, provides
#						the methods to get the additional parameters
#						that are required from some arguments.
#	
#	2) help:			Contains the "help" messages for each
#						argument. Also, provides the methods to print
#						the help messages.
#
#	3) error_messages: 	Contains the error_messages for the
#						user-errors that might occur. Also, provides
#						the methods to print the error messages.
#
#	4) error:			Contains the error values that correspond
#						to the user-errors. Also, some methods to
#						check if such an error occured.
#
#	5) about:			Contains information regarding this version
#						of the application. Also, provides the method
#						to print this about message.
#
#	6) Application:		Uses all the classes above, determines the
#						state defined from the user (by the arguments),
#						and makes the correct calls to the methods
#						of the AdaptationProcedure class of
#						adaptation_procedure.py.
# 
#
# author: Merkouris Papamichail
# email: mercoyris@ics.forth.gr
# institute: ICS, FORTH
# last update: 13/4/2022
#####################################################################


#############
# Libraries #
#############

## Python Libraries
from os import path
import random

## Custom Libraries
import adaptation_procedure as ap
import gambit
import debugging
import domain
#import multithread_nash_equilibria
#import multithread_clingo_calls

## 3rd party libraries
from termcolor import colored, cprint

#############
# Arguments #
#############

class args:
	file			= "-f"		# initialize root from file
								# e.g.: -f <mg file path>
	random			= "-r"		# generate a random root
								# e.g.:  -r <num_players> <strat_1> <strat_2> ... <strat_n> <max_util>
	seed			= "-se"		# The seed for the random number generator, e.g. -se 0
								# Relevant, only if -r parameter has been given,
								# otherwise discarded.
	tree			= "-t"		# print the tree
	root			= "-ro"		# print the root
	save_tree		= "-st"		# save tree to file
	leaves			= "-l"		# print the leaves
	nodes			= "-n"		# print all the nodes
	uniq_mgs		= "-m"		# print the uniqe MGs
	sav_uniq_mgs	= "-sm"		# save the unique MGs under a diretory.
								# e.g.: -sm <dir_path>
	sav_stable_set	= "-ss" 	# save stable set, the unique .mg files under a directory
								# e.g.: -ss <dir_path>
	save_root		= "-sr"		# save the root to file
	help			= "-h"		# prints list of arguments
	quiet			= "-q"		# suppress the "about" header
	no_out			= "-no" 	# suppresses ALL output, useful for experiments
	fast_mode		= "-fm" 	# fast mode, discards duplicate mgs, doesnt explore the hole minimal adaptation tree
	NE_method		= "-nem"	# specify the method for computing Nash Equilibria
								# e.g. -nem xpe, for computing NE using extreme point
								# 	enumeration (gambit-enummixed) Note: Works only for
								#	2-player games.
								# -nem gnm, for computing NE using the General Newton
								# 	Method (gambit-gnm) Note: Works for general
								#	n-player games.
	debug			= "-dbg"	# Additional statistics for debugging and a deeper monitoring
								# of the process. The user can provide additional arguments,
								# -dbg p or -dbg d, for printing the warnings, or kill (die)
								# the application after a warning.
	domain			= "-dmn"	# Specifies the domain of the strategy profiles
								# e.g. -dmn v, for voronoi, -dmn r, for "real", leaving the
								# input unchanged. If this argument is not given, the default
								# behaviour is -dmn r
	mul_thred_NE	= "-mtn"	# Enforces multithreading for computing in parallel the
								#	nash equilibria for the n + 1 NFGs of a MG.
	mul_thred_cl	= "-mtc"	# Enforces multithreading for computing in parallel the
								# the clingo calls, e.g. -mtc <number of threads>
	mul_thred_tr	= "-mtt"	# Multithreading Traversal. Exploring the Adaptation Graph,
								# in parallel.

	## Methods
	# Predicates
	def is_init_from_file(self, argv):
		return self.file in argv
	
	def is_init_rand(self, argv):
		return self.random in argv
	
	def is_seed(self, argv):
		return self.seed in argv
	
	def is_print_tree(self, argv):
		return self.tree in argv
	
	def is_root(self, argv):
		return self.root in argv
	
	def is_save_tree(self, argv):
		return self.save_tree in argv
	
	def is_print_leaves(self, argv):
		return self.leaves in argv
	
	def is_print_nodes(self, argv):
		return self.nodes in argv
	
	def is_uniq_mgs(self, argv):
		return self.uniq_mgs in argv
	
	def is_sav_uniq_mgs(self, argv):
		return self.sav_uniq_mgs in argv
	
	def is_sav_stable_set(self, argv):
		return self.sav_stable_set in argv
	
	def is_save_root(self, argv):
		return self.save_root in argv
	
	def is_help(self, argv):
		return self.help in argv
	
	def is_quiet(self, argv):
		return self.quiet in argv
	
	def is_no_out(self, argv):
		return self.no_out in argv
	
	def is_fast_mode(self, argv):
		return self.fast_mode in argv

	def is_NE_method(self, argv):
		return self.NE_method in argv

	def is_debug(self, argv):
		return self.debug in argv

	def is_domain(self, argv):
		return self.domain in argv

	def is_mul_thred_NE(self, argv):
		return self.mul_thred_NE in argv

	def is_mul_thred_cl(self, argv):
		return self.mul_thred_cl in argv

	def is_mul_thred_tr(self, argv):
		return self.mul_thred_tr in argv

	# Acquire Data
	# In order to correctly call the following methods
	# the errors.check_all(argv) should be called first
	def get_init_file(self, argv):
		assert self.is_init_from_file(argv)
		
		ind = argv.index(self.file)
		return argv[ind + 1]
	
	def get_seed(self, argv):
		ind = argv.index(self.seed)
		return argv[ind + 1]
	
	def get_num_players(self, argv):
		assert self.is_init_rand(argv)
		
		ind = argv.index(self.random)
		return int(argv[ind + 1])
	
	def get_strategies_vec(self, argv):
		assert self.is_init_rand(argv)
		
		ind = argv.index(self.random)
		num_players = self.get_num_players(argv)
		strategies = []
		for i in range(ind + 2, ind + 2 + num_players):
			strategies.append(int(argv[i]))
		
		return strategies
	
	def get_max_util(self, argv):
		assert self.is_init_rand(argv)
		
		ind = argv.index(self.random)
		num_players = self.get_num_players(argv)
		return int(argv[ind + 1 + num_players + 1])
	
	def get_uniq_mg_dir(self, argv):
		assert self.is_sav_uniq_mgs(argv)
		
		ind = argv.index(self.sav_uniq_mgs)
		return argv[ind + 1]
	
	def get_stable_set_dir(self, argv):
		assert self.is_sav_stable_set(argv)
		
		ind = argv.index(self.sav_stable_set)
		return argv[ind + 1]
	
	def get_save_tree_path(self, argv):
		assert self.is_save_tree(argv)
		
		ind = argv.index(self.save_tree)
		return argv[ind + 1]
	
	def get_save_root_path(self, argv):
		assert self.is_save_root(argv)
		
		ind = argv.index(self.save_root)
		return argv[ind + 1]

	def get_NE_method(self, argv):
		assert self.is_NE_method(argv)

		ind = argv.index(self.NE_method)
		return argv[ind+1]

	def get_debug_params(self, argv):
		assert self.is_debug(argv)

		ind = argv.index(self.debug)
		params = []

		# check for the optional parameters
		if (ind + 1 <= len(argv) - 1) and (argv[ind + 1][0] != "-"):
			params.append(argv[ind + 1])

		if (ind + 2 <= len(argv) - 1) and (argv[ind + 1][0] != "-") and (argv[ind + 2][0] != "-"):
			params.append(argv[ind + 2])


		return params

	def get_domain_method(self, argv):
		assert self.is_domain(argv)

		ind = argv.index(self.domain)
		return argv[ind + 1]

	def get_domain_decimal(self, argv):
		assert self.is_domain(argv)
		assert domain_methods.decimal == self.get_domain_method(argv)

		ind = argv.index(self.domain)
		return argv[ind + 2]

	def get_mul_thred_cl_num_threads(self, argv):
		assert self.is_mul_thred_cl(argv)

		ind = argv.index(self.mul_thred_cl)
		return argv[ind + 1]


	def get_num_trversal_threads(self, argv):
		assert self.is_mul_thred_tr(argv)

		ind = argv.index(self.mul_thred_tr)
		return argv[ind + 1]


args = args()

arg_list = [
		args.file,
		args.random,
		args.seed,
		args.tree,
		args.root,
		args.save_tree,
		args.leaves,
		args.nodes,
		args.uniq_mgs,
		args.sav_uniq_mgs,
		args.sav_stable_set,
		args.save_root,
		args.help,
		args.quiet,
		args.no_out,
		args.fast_mode,
		args.NE_method,
		args.debug,
		args.domain,
		args.mul_thred_tr
		#args.mul_thred_NE,
		#args.mul_thred_cl
	]

## Available methods for the debug command
class debug_params:
	print_warnings		= "p"
	die_after_warning	= "d"

debug_params_list = [
	debug_params.print_warnings,
	debug_params.die_after_warning
]



## Available Methods for computing Nash Equilibria
class NE_methods:
	enummixed	= "xpe"	# Extreme Point Enumeration
	gnm			= "gnm"	# Generalized Newton Method
	enp			= "enp" # Enumerate Pure Equilibria
	pol			= "pol"	# Compute NE by Support Enumeration

NE_methods_list = [
	NE_methods.enummixed,
	NE_methods.gnm,
	NE_methods.enp,
	NE_methods.pol
]

class domain_methods:
	real	= "r"
	voronoi	= "v"
	decimal	= "d"

domain_method_list = [
	domain_methods.real,
	domain_methods.voronoi,
	domain_methods.decimal
]

class help:
	file		= "Initialize root from file, e.g.: -f <mg file path>."
	random		= "Generate a random root, \n\
	e.g.:  -r <num_players> <strat_1> <strat_2> ... <strat_n> <max_util>."
	seed		= "The seed for the random number generator, e.g. -se 10.\n\
	Relevant, only if -r parameter has been given, otherwise discarded.\n\
	Default value 0."
	tree		= "Print the Adaptation Tree (text-based figure)."
	root		= "Print the root of the Adaptation Procedure."
	save_tree	= "Save the Adaptation Tree (text-based figure) to file, e.g. -st <path>."
	leaves		= "Print the list of Adaptation Tree leaf nodes."
	nodes		= "Print all the Adaptation Tree nodes."
	uniq_mgs	= "Print the set of the unique Misinformation Games."
	sav_uniq_mgs= "Save the unique MGs under a directory as .mg files.\n\
	e.g.: -sm <dir_path>"
	sav_stable_set="Save stable set, the unique .mg files under a directory.\n\
	e.g.: -ss <dir_path>"
	save_root	= "Save the root MG to file, e.g. -sr <path>."
	help		= "Prints this list of arguments."
	quiet		= "Suppresses the \"about\" header, and the \"stats\" section."
	no_out		= "Suppresses ALL output, useful for experiments."
	fast_mode	= "Fast mode, discards duplicate MGs. Doesn't explore the whole\n\
	adaptation tree. Considers all the unique MGs."
	NE_method	= "Specifies the method for computing Nash Equilibria.\n\
	e.g. -nem xpe, for computing NE using extreme point\n\
	enumeration (gambit-enummixed). Other methods supported are gnm, enp, pol"
	debug		= "Additional statistics for debugging and a deeper monitoring\n\
	of the process. The user can provide additional arguments,\n\
	-dbg " + debug_params.print_warnings + " or -dbg " + debug_params.die_after_warning + ", for printing the warnings, or kill (die)\n\
	the application after a warning."
	domain		= "Specifies the domain of the strategy profiles\n\
	e.g. -dmn v, for voronoi, -dmn r, for \"real\", leaving the\n\
	input unchanged. If this argument is not given, the default\n\
	behaviour is -dmn r"
	#mul_thred_NE = "Enforces multithreading for computing in parallel the\n\   DEPRICATED COMMANDS (DO NOT USE)
	#nash equilibria for the n + 1 NFGs of a MG."
	#mul_thred_cl = "Enforces multithreading for computing in parallel the\n\   DEPRICATED COMMANDS (DO NOT USE)
	#the clingo calls, e.g. -mtc <number of threads>"
	mul_thred_tr = "Multithreading Traversal. Exploring the Adaptation Graph,\n\
	in parallel. (Only Available in Fast Mode!)"


	## Print Help
	def print_help(self):
		print(args.file + "\t" + self.file)
		print(args.random + "\t" + self.random)
		print(args.seed + "\t" + self.seed)
		print(args.tree + "\t" + self.tree)
		print(args.root + "\t" + self.root)
		print(args.save_tree + "\t" + self.save_tree)
		print(args.leaves + "\t" + self.leaves)
		print(args.nodes + "\t" + self.nodes)
		print(args.uniq_mgs + "\t" + self.uniq_mgs)
		print(args.sav_uniq_mgs + "\t" + self.sav_uniq_mgs)
		print(args.sav_stable_set + "\t" + self.sav_stable_set)
		print(args.save_root + "\t" + self.save_root)
		print(args.help + "\t" + self.help)
		print(args.quiet + "\t" + self.quiet)
		print(args.no_out + "\t" + self.no_out)
		print(args.fast_mode + "\t" + self.fast_mode)
		print(args.NE_method + "\t" + self.NE_method)
		print(args.debug + "\t" + self.debug)
		print(args.domain + "\t" + self.domain)
		#print(args.mul_thred_NE + "\t" + self.mul_thred_NE)    DEPRICATED COMMANDS (DO NOT USE)
		#print(args.mul_thred_cl + "\t" + self.mul_thred_cl)    DEPRICATED COMMANDS (DO NOT USE)
		print(args.mul_thred_tr + "\t" + self.mul_thred_tr)

help = help()

class error_messages:
	## Error Prefix
	prefix					= "Error: "
	
	## Error Suffix
	suffix					= "!"
	
	## Suggestion
	suggestion				= "Use the argument -h for help."
	
	## Error Messages
	no_init_params			= "Neither \"-f\" nor \"-r\" parametes provided"
	in_file_not_found		= "In -f <path> the file in <path> not found"
	file_no_path			= "In -f no path provided"
	random_error			= "The -r command doesn't follow the correct syntax"
	sav_root_no_path		= "In -sr <path> no path provided"
	sav_tree_no_path		= "In -st <path> no path provided"
	too_many_init_params	= "Both -f and -r provided"
	unknown_param			= "An parameter passed that is not a member of arg_list"
	seed_error				= "The -se command provided with no value"
	no_mg_dir				= "In -sm <dir_path> either no path provided, or the path is not a directory"
	no_ss_dir				= "In -ss <dir_path> either no path provided, or the path is not a directory"
	NE_no_method			= "In -nem <method>, no method provided"
	NE_unknown_method		= "In -nem <method>, unknown method provided"
	debug_unknown_method	= "In -dbg <params>, unknown parameters provided"
	dmn_no_method			= "In -dmn <method>, no method provided"
	dmn_unkown_method		= "In -dmn <method>, unknown method provided"
	dmn_dec_no_dec			= "In -dmn d <decimal points> no decimal points provided"
	mtc_no_threads_num		= "In -mtc <threads number>, no threads number provided"
	mtt_no_threads_num		= "In -mtt <threads number>, no threads number provided"
	mtt_in_slow_mode		= "Multithreading is available ONLY in fast mode"
	
class errors:
	no_init_params			= 1		# no -r or -f parameters provided
	in_file_not_found		= 2		# in -f <path> the file in <path> not found
	file_no_path			= 3		# in -f no path provided
	random_error			= 4		# the -r command doesn't follow the correct syntax
	sav_root_no_path		= 5		# in -sr no path provided
	sav_tree_no_path		= 6		# in -st no path provided
	too_many_init_params	= 7		# both -f and -r provided or too many -f or -r
	unknown_param			= 8		# a parameter passed that is not a member of arg_list
	seed_error				= 9		# The -se command provided with no value
	no_mg_dir				= 10	# In -sm <dir_path> either no path provided, or the path is not a directory
	no_ss_dir				= 11	# In -ss <dir_path> either no path provided, or the path is not a directory
	NE_no_method			= 12	# In -nem <method>, no method provided
	NE_unknown_mehtod		= 13	# In -nem <method>, unknown method provided
	debug_unknown_method	= 14	# In -dbg <params>, unknown parameters provided
	dmn_no_method			= 15	# In -dmn <method>, no method provided
	dmn_unkown_method		= 16	# In -dmn <method>, unknown method provided
	dmn_dec_no_dec			= 17	# In -dmn d <decimal poiuunts> no decimal points provided
	mtc_no_threads_num		= 18	# In -mtc <threads number>, no threads number provided
	mtt_no_threads_num		= 19	# In -mtt <threads number>, no threads number provided
	mtt_in_slow_mode		= 20	# Multithreading is available ONLY in fast mode
	
	## One check to rule them all
	def check_all(self, argv):
		
		if not self.check_no_init_params(argv):
			print(error_messages.prefix + error_messages.no_init_params + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.no_init_params)
		
		if not self.check_in_file_not_foud(argv):
			print(error_messages.prefix + error_messages.in_file_not_found + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.in_file_not_found)
		
		if not self.check_file_no_path(argv):
			print(error_messages.prefix + error_messages.file_no_path + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.file_no_path)
		
		if not self.check_random_error(argv):
			print(error_messages.prefix + error_messages.random_error + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.random_error)
		
		if not self.check_sav_root_no_path(argv):
			print(error_messages.prefix + error_messages.sav_root_no_path + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.sav_root_no_path)
		
		if not self.check_sav_tree_no_path(argv):
			print(error_messages.prefix + error_messages.sav_tree_no_path + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.sav_tree_no_path)
		
		if not self.check_too_many_init_params(argv):
			print(error_messages.prefix + error_messages.too_many_init_params + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.too_many_init_params)
		
		if not self.check_unkown_param(argv):
			print(error_messages.prefix + error_messages.unknown_param + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.unknown_param)
	
		if not self.check_seed_error(argv):
			print(error_messages.prefix + error_messages.seed_error + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.seed_error)
		
		if not self.check_no_mg_dir(argv):
			print(error_messages.prefix + error_messages.no_mg_dir + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.no_mg_dir)
		
		if not self.check_no_ss_dir(argv):
			print(error_messages.prefix + error_messages.no_ss_dir + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.no_ss_dir)

		if not self.check_NE_no_method(argv):
			print(error_messages.prefix + error_messages.NE_no_method + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.NE_no_method)

		if not self.check_NE_unknown_method(argv):
			print(error_messages.prefix + error_messages.NE_unknown_method + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.NE_unknown_mehtod)

		if not self.check_debug_unknown_params(argv):
			print(error_messages.prefix + error_messages.debug_unknown_method + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.debug_unknown_method)

		if not self.check_domain_no_method(argv):
			print(error_messages.prefix + error_messages.dmn_no_method + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.dmn_no_method)

		if not self.check_domain_unknown_method(argv):
			print(error_messages.prefix + error_messages.dmn_unkown_method + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.dmn_unkown_method)

		if not self.check_decimal_no_dec(argv):
			print(error_messages.prefix + error_messages.dmn_dec_no_dec + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.dmn_dec_no_dec)

		if not self.check_mtc_no_threads_num(argv):
			print(error_messages.prefix + error_messages.mtc_no_threads_num + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.mtc_no_threads_num)

		if not self.check_mtt_no_threads_num(argv):
			print(error_messages.prefix + error_messages.mtt_no_threads_num + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.mtt_no_threads_num)

		if not self.check_mtt_in_slow_mode(argv):
			print(error_messages.prefix + error_messages.mtt_in_slow_mode + error_messages.suffix)
			print(error_messages.suggestion)
			exit(self.mtt_in_slow_mode)
	
	## Check for Errors
	def check_no_init_params(self, argv):
		return (args.file in argv) or (args.random in argv)
	
	
	def check_in_file_not_foud(self, argv):
		
		if args.file not in argv: return True		# if -f not in argv the check is true by default
		
		ind = argv.index(args.file)					# get the index of -f
		
		if ind + 1 > len(argv) - 1: return False	# if there is no argument succeeding -f, return False
		
		file_path = argv[ind + 1]					# get the file path
		return path.exists(file_path)				# return if path exists
	
	
	
	def check_file_no_path(self, argv):
				
		if args.file not in argv: return True		# if -f not in argv the check is true by default
		
		ind = argv.index(args.file)					# get the index of -f
			
		if ind + 1 > len(argv) - 1:	return False	# if there is no argument succeeding -f, return False
		
		file_path = argv[ind + 1]					# get the file path
		return file_path[0] != "-"					# return if the succeeding argument is another parameter
	
	
	
	def check_random_error(self, argv):
		
		if args.random not in argv: return True			# if -r not in argv the check is true by default
		
		ind = argv.index(args.random)					# get the index of -r
			
		if ind + 1 > len(argv) - 1: return False		# if there is no argument succeeding -r, return False
		
		if not argv[ind + 1].isdecimal(): return False	# if the succeeding argument is no number return False
		
		num_players = int(argv[ind + 1])				# get the number of players

		# check if every succeeding argument *is* a number
		# strat_ind = ind + 2
		for i in range(ind + 1, ind + num_players + 2 + 1):
			if i > len(argv) - 1: return False
			if not argv[i].isdecimal(): return False

		# check if there are *too* many succeeding arguments
		# (in case of too few the previous check returns False)
		if ind + 2 + num_players + 1 >= len(argv):
			return True
		else:
			return argv[ind + 2 + num_players + 1][0] == "-"
	
	
	def check_sav_root_no_path(self, argv):
		
		if args.save_root not in argv: return True
		
		ind = argv.index(args.save_root)
		
		if ind + 1 > len(argv) - 1: return False
		
		file_path = argv[ind + 1]				# get the file path
		return file_path[0] != "-"				# return if path exists
	
	
	
	def check_sav_tree_no_path(self, argv):
		
		if args.save_tree not in argv: return True
		
		ind = argv.index(args.save_tree)
		
		if ind + 1 > len(argv) - 1: return False
		
		file_path = argv[ind + 1]					# get the file path
		return file_path[0] != "-"				# return if path exists
	
	
	def check_too_many_init_params(self, argv):
		
		return not ( (args.random in argv) and (args.file in argv) )
	
	
	def check_unkown_param(self, argv):
		
		for arg in argv:
			if arg[0] == "-" and arg not in arg_list: return False
		
		return True
	
	def check_seed_error(self, argv):
		
		if args.seed not in argv: return True
		
		ind = argv.index(args.seed)
		if ind + 1 > len(argv) - 1: return False
		
		return argv[ind + 1].isdecimal()
	
	def check_no_mg_dir(self, argv):
		if not args.is_sav_uniq_mgs(argv): return True
		
		ind = argv.index(args.sav_uniq_mgs)
		if ind + 1 > len(argv) - 1: return False
		
		return path.isdir(argv[ind + 1])
	
	def check_no_ss_dir(self, argv):
		if not args.is_sav_stable_set(argv): return True
		
		ind = argv.index(args.sav_stable_set)
		if ind + 1 > len(argv) - 1: return False
		
		return path.isdir(argv[ind + 1])

	def check_NE_no_method(self, argv):
		if not args.is_NE_method(argv): return True

		ind = argv.index(args.NE_method)
		if ind + 1 > len(argv) - 1: return False

		method = argv[ind + 1]
		return method != "-"

	def check_NE_unknown_method(self, argv):
		if not args.is_NE_method(argv): return True

		ind = argv.index(args.NE_method)
		if ind + 1 > len(argv) - 1: return False

		method = argv[ind + 1]
		return method in NE_methods_list

	def check_debug_unknown_params(self, argv):
		if not args.is_debug(argv): return True

		ind = argv.index(args.debug)
		condition = True

		# check for the optional parameters
		if (ind + 1 <= len(argv) - 1) and (argv[ind + 1][0] != "-"):
			condition = condition and ( argv[ind + 1] in debug_params_list )

		if (ind + 2 <= len(argv) - 1) and (argv[ind + 1][0] != "-") and (argv[ind + 2][0] != "-"):
			condition = condition and ( argv[ind + 2] in debug_params_list )

		return condition

	def check_domain_no_method(self, argv):
		if not args.is_domain(argv): return True

		ind = argv.index(args.domain)
		if ind + 1 > len(argv) - 1: return False
		if argv[ind + 1][0] == "-": return False

		return True

	def check_domain_unknown_method(self, argv):
		if not args.is_domain(argv): return True

		ind = argv.index(args.domain)
		if ind + 1 > len(argv) - 1: return False

		method = argv[ind + 1]
		return method in domain_method_list

	def check_decimal_no_dec(self, argv):
		if not args.is_domain(argv): return True

		ind = argv.index(args.domain)
		if ind + 1 > len(argv) - 1: return False

		method = argv[ind + 1]
		if method != domain_methods.decimal: return True

		if ind + 2 > len(argv) - 1: return False
		return argv[ind + 2].isdecimal()

	def check_mtc_no_threads_num(self, argv):
		if not args.is_mul_thred_cl(argv): return True

		ind = argv.index(args.mul_thred_cl)
		if ind + 1 > len(argv) - 1: return False

		num_threads = argv[ind + 1]
		return num_threads.isdecimal()

	def check_mtt_no_threads_num(self, argv):
		if not args.is_mul_thred_tr(argv): return True

		ind = argv.index(args.mul_thred_tr)
		if ind + 1 > len(argv) - 1: return False

		num_threads = argv[ind + 1]
		return num_threads.isdecimal()

	def check_mtt_in_slow_mode(self, argv):
		return args.is_fast_mode(argv) or not args.is_mul_thred_tr(argv)

err = errors()
	

class about:
	description	= "Misinformation Games Adaptation Procedure"
	version		= "Version 2.0"
	author		= "Author: Merkouris Papamichail"
	email		= "Email: mercoyris@ics.forth.gr"
	copyright	= "Copyright FORTH 2022"
	
	## Print About section
	def print_about(self):
		print(self.description)
		print(self.version)
		print(self.author)
		print(self.email)
		print(self.copyright + "\n")

about = about()



class Application:
	
	## State (Boolean)
	from_file		= False
	random			= False
	seed			= False
	tree			= False
	root			= False
	save_tree		= False
	leaves			= False
	nodes			= False
	uniq_mgs		= False
	sav_uniq_mgs	= False
	sav_stable_set	= False
	save_root		= False
	help			= False
	quiet			= False
	no_out			= False
	fast_mode		= False
	NE_method		= False
	debug 			= False
	domain			= False
	mul_thred_NE	= False
	mul_thread_cl	= False
	mul_thread_tr	= False
	
	## Data
	in_file_path 	= None
	seed_val		= None
	num_players		= None
	strategies		= None
	max_util		= None
	sav_tree_path	= None
	sav_root_path	= None
	uniq_mgs_dir	= None
	st_set_dir		= None
	method			= None
	params			= None
	dmn_method		= None
	dmn_decimal		= None
	mtc_num_threads	= None
	mtt_num_threads	= None
	
	
	## Adaptation Procedure
	adapt_proc = None

	## GAMBIT package
	gambit_pac = None

	## Debugging class
	debugging = None

	## Domain class
	strat_prof_domain = None

	## Multithreading Nash Equilibria
	multithread_NE = None

	## Multithreading CLINGO calls
	multithread_cl = None

	## class states
	adaptation_procedure_done = False
	
	########
	# Init #
	########
	def __init__(self, argv):
		
		## -h help exception
		if args.is_help(argv):
			self.help = args.is_help(argv)
			self.quiet = args.is_quiet(argv)
			return
		
		#########
		# Check #
		#########
		err.check_all(argv)
		
		
		
		#########
		# State #
		#########
		self.from_file		= args.is_init_from_file(argv)
		self.random			= args.is_init_rand(argv)
		self.seed			= args.is_seed(argv)
		self.tree			= args.is_print_tree(argv)
		self.root			= args.is_root(argv)
		self.save_tree		= args.is_save_tree(argv)
		self.leaves			= args.is_print_leaves(argv)
		self.nodes			= args.is_print_nodes(argv)
		self.uniq_mgs		= args.is_uniq_mgs(argv)
		self.sav_uniq_mgs 	= args.is_sav_uniq_mgs(argv)
		self.sav_stable_set	= args.is_sav_stable_set(argv)
		self.save_root		= args.is_save_root(argv)
		self.help			= args.is_help(argv)
		self.quiet			= args.is_quiet(argv)
		self.no_out			= args.is_no_out(argv)
		self.fast_mode		= args.is_fast_mode(argv)
		self.NE_method		= args.is_NE_method(argv)
		self.debug			= args.is_debug(argv)
		self.domain			= args.is_domain(argv)
		#self.mul_thred_NE	= args.is_mul_thred_NE(argv)
		#self.mul_thread_cl	= args.is_mul_thred_cl(argv)
		self.mul_thread_tr	= args.is_mul_thred_tr(argv)
		
		
		
		########
		# Data #
		########
		# if any get init file
		if self.from_file: self.in_file_path = args.get_init_file(argv)
		
		# if init randomly, get the necessary data from args
		if self.random:
			self.num_players	= args.get_num_players(argv)
			self.strategies		= args.get_strategies_vec(argv)
			self.max_util		= args.get_max_util(argv)
		
		# if seed, get seed
		self.seed_val = 0
		if self.seed: self.seed_val = int(args.get_seed(argv))
		random.seed(self.seed_val)
			
		
		# if applicable, get save tree path
		if self.save_tree: self.sav_tree_path = args.get_save_tree_path(argv)
		
		# if applicable, get the save root path
		if self.save_root: self.sav_root_path = args.get_save_root_path(argv)
		
		# if applicable, get the save unique mgs dir path
		if self.sav_uniq_mgs: self.uniq_mgs_dir = args.get_uniq_mg_dir(argv)
		
		if self.sav_stable_set: self.st_set_dir = args.get_stable_set_dir(argv)
		
		## Choose GAMBIT method for computing Nash Equilibria for Normal Form Games
		if self.NE_method:
			self.method = args.get_NE_method(argv)
		else:
			self.method = NE_methods.pol			# The Default NE Method is gambit-enumpoly

		# debugging
		if self.debug:
			self.params = args.get_debug_params(argv)

		##########
		# Domain #
		##########
		gambit_decimals = 8
		dmn_method = domain.domain_methods_vals.real
		if self.domain:
			self.dmn_method = args.get_domain_method(argv)

			if self.dmn_method == domain_methods.real:
				dmn_method = domain.domain_methods_vals.real

			if self.dmn_method == domain_methods.voronoi:
				dmn_method = domain.domain_methods_vals.voronoi

			if self.dmn_method == domain_methods.decimal:
				dmn_method = domain.domain_methods_vals.real

				gambit_decimals = int(args.get_domain_decimal(argv))


		self.strat_prof_domain = domain.SPDomain(dmn_method)


		##########
		# GAMBIT #
		##########
		
		# Choose the method for computing Nash Equilibria for Normal Form Games,
		# from the available GAMBIT methods
		
		if self.method == NE_methods.gnm:
			self.gambit_pac = gambit.Gambit(gambit_decimals, gambit.method_vals.gnm_val)

		if self.method == NE_methods.enummixed:
			self.gambit_pac = gambit.Gambit(gambit_decimals, gambit.method_vals.xpe_val)

		if self.method == NE_methods.enp:
			self.gambit_pac = gambit.Gambit(gambit_decimals, gambit.method_vals.enp_val)

		if self.method == NE_methods.pol:
			self.gambit_pac = gambit.Gambit(gambit_decimals, gambit.method_vals.pol_val)


		#############
		# Debugging #
		#############

		# NOTE: We always create a Debugging instance whether the user
		# provides the -dbg command, or not. In case the -dbg command
		# is not provided, we just don't print the extended statistics.

		dbg_print_warnings		= False
		dbg_die_after_warning	= False

		if self.debug:
			dbg_print_warnings		= debug_params.print_warnings in self.params
			dbg_die_after_warning	= debug_params.die_after_warning in self.params

		self.debugging = debugging.Debugging(dbg_print_warnings, dbg_die_after_warning)

		##########
		# Domain #
		##########
		dmn_method = domain.domain_methods_vals.real
		if self.domain:
			self.dmn_method = args.get_domain_method(argv)

			if self.dmn_method == domain_methods.real:
				dmn_method = domain.domain_methods_vals.real

			if self.dmn_method == domain_methods.voronoi:
				dmn_method = domain.domain_methods_vals.voronoi

		self.strat_prof_domain = domain.SPDomain(dmn_method)

		##################################
		# Multithreading Nash Equilibria #
		##################################

		#self.multithread_NE = multithread_nash_equilibria.MultithreadNashEquilibria(self.mul_thred_NE)

		###############################
		# Multithreading CLINGO calls #
		###############################

		#self.multithread_cl = multithread_clingo_calls.MultithreadClingoCalls(self.mul_thread_cl)

		#clingo_calls_num_threads = 1
		#if self.mul_thread_cl:
		#	clingo_calls_num_threads = int(args.get_mul_thred_cl_num_threads(argv))


		########################
		# Adaptation Procedure #
		########################
		#print("inti_adapt_proc_application")
		self.mtt_num_threads = 1
		if self.mul_thread_tr:
			self.mtt_num_threads = int(args.get_num_trversal_threads(argv))
		self.debugging.check_num_threads(self.mtt_num_threads)

		self.adapt_proc = ap.AdaptationProcedure(
			self.gambit_pac,
			self.debugging,
			self.strat_prof_domain,
			self.mtt_num_threads,
			self.quiet,
			self.fast_mode
		)
		
		## Initialize from file
		if args.is_init_from_file(argv):
			f = open(self.in_file_path, "r")
			file_fmt = f.read()
			f.close()
			
			self.adapt_proc.root_from_file(file_fmt)
		
		## Initialize random
		else:
			self.adapt_proc.root_random(self.num_players, self.strategies, self.max_util)
			#print("application")

		
	###############
	# Accessors #
	###############
	
	def get_is_adaptation_concluded(self):
		return self.adapt_proc.adaptation_procedure_completed
	
	def get_total_mgs(self):
		return self.adapt_proc.get_total_mgs()
	
	def get_progress_computed_mgs(self):
		return self.adapt_proc.get_progress_computed_mgs()
	
	def get_stats(self):
		assert self.adaptation_procedure_done == True
		
		adapt_proc_stats = self.adapt_proc.get_stats()
		debugging_stats = self.debugging.get_stats()
		
		stats = adapt_proc_stats
		if self.debug:
			stats += debugging_stats
			
		return stats
		
	def get_numerical_stats(self):
		assert self.adaptation_procedure_done == True
		
		adapt_proc_stats = self.adapt_proc.get_stats()
		# debugging_stats = self.debugging.get_stats()
		
		stats = adapt_proc_stats[0:1]
		stats += adapt_proc_stats[3:]
		
		# print(stats)
		
		return stats
	
	
	#########
	# Print #
	#########
	
	# For debugging
	def print(self):
		## State
		print("from_file = " + str(self.from_file))
		print("random = " + str(self.random)) 
		print("tree = " + str(self.tree))
		print("root = " + str(self.root))
		print("save_tree = " + str(self.save_tree))
		print("leaves = " + str(self.tree))
		print("nodes = " + str(self.nodes))
		print("uniq_mgs = " + str(self.uniq_mgs))
		print("sav_uniq_mgs = " + str(self.sav_uniq_mgs))
		print("sav_stable_set = " + str(self.sav_stable_set))
		print("save_root = " + str(self.save_root))
		print("help = " + str(self.help))
		print("quiet = " + str(self.quiet))
		print("no out = " + str(self.no_out))
		print("fast mode = " + str(self.fast_mode))
		print("NE_method = " + str(self.NE_method))
		print("debugging = " + str(self.debug))
		print("domain = " + str(self.domain))
	
		## Data
		print("in_file_path = " + str(self.in_file_path))
		print("num_players = " + str(self.num_players))
		print("strategies = " + str(self.strategies))
		print("max_util = " + str(self.max_util))
		print("sav_tree_path = " + str(self.sav_tree_path))
		print("sav_root_path = " + str(self.sav_root_path))
		print("uniq_mgs_dir = " + str(self.uniq_mgs_dir))
		print("st_set_dir = " + str(self.st_set_dir))
		print("method = " + str(self.method))
		print("dmn_method = " + str(self.dmn_method))


	##############
	# Statistics #
	##############

	def print_stats(self):
		print(self.export_stats())
	#	assert self.adaptation_procedure_done == True
	#
	#	adapt_proc_stats = self.adapt_proc.get_stats()

	#	print("+" + 39 * "-")
	#	print("| Number of players: " + str(adapt_proc_stats[0]))
	#	print("| Strategies Vector: " + str(adapt_proc_stats[1]))
	#	print("| NE Method: " + adapt_proc_stats[2])
	#	print("| Number of Threads: " + str(self.mtt_num_threads))

	#	init_method = "| Initialization Method: "
	#	if self.random: init_method += "Random"
	#	else: init_method += "File: " + self.in_file_path
	#	print(init_method)

	#	print("| Seed: " + str(self.seed_val))
	#	if self.max_util: print("| Max Util: " + str(self.max_util))
	#	print("+" + "-" * 39)
	#	print("| Total: " + str(round(adapt_proc_stats[3], 2)) + "(s)")
	#	print("| CPU time: " + str(round(adapt_proc_stats[4], 2)) + "(s)")
	#	print("| Number of nodes: " + str(adapt_proc_stats[5]))
	#	print("| Number of unique MGs: " + str(adapt_proc_stats[6]))
	#	print("| Number of leaves: " + str(adapt_proc_stats[7]))
	#	print("| Number of Unique Terminal Games: " + str(adapt_proc_stats[8]))
	#	print("| Number of SMEs: " + str(adapt_proc_stats[9]))

	#	print("+" + 39 * "-")
	#	if self.debug:
	#		debug_stats = self.debugging.get_stats()
	#		print("| Total GAMBIT time: " + str(round(debug_stats[0], 2)) + "(s)")
	#		print("| Number of GAMBIT calls: " + str(debug_stats[1]))
	#		print("| Average time per GAMBIT call: " + str(round(debug_stats[2], 3)) + "(s)")
	#		print("| Total CLINGO time: " + str(round(debug_stats[3], 2)) + "(s)")
	#		print("| Number of CLINGO calls: " + str(debug_stats[4]))
	#		print("| Average time per CLINGO call: " + str(round(debug_stats[5], 3)) + "(s)")
	#		print("+" + 39 * "-")
	#		print("| GAMBIT time / Total Time %: " + str(round(debug_stats[0] / adapt_proc_stats[3] * 100, 2)) + "%")
	#		print("| CLINGO time / Total Time %: " + str(round(debug_stats[3] / adapt_proc_stats[3] * 100, 2)) + "%")
	#		print("| CPU time / Total Time %: " + str(round(adapt_proc_stats[4] / adapt_proc_stats[3] * 100, 2)) + "%")
	#		print("+" + 39 * "-")
	#		print("| # Zeros Mixed Strategy: " + str(debug_stats[6]))
	#		print("| # Mixed Strategies \w sum <= 1: " + str(debug_stats[7]))
	#		print("| # No NE after GAMBIT call: " + str(debug_stats[8]))
	#		print("| Too many threads: " + str(debug_stats[9]))
	#		print("+" + 39 * "-")
	
	def export_stats(self):
		assert self.adaptation_procedure_done == True

		adapt_proc_stats = self.adapt_proc.get_stats()
		
		output = ""
		output += "+" + 60 * "-" + "\n"
		output += "| Number of players: " + str(adapt_proc_stats[0]) 	+ "\n"
		output += "| Strategies Vector: " + str(adapt_proc_stats[1])	+ "\n"
		output += "| NE Method: " + adapt_proc_stats[2]					+ "\n"
		output += "| Number of Threads: " + str(self.mtt_num_threads)	+ "\n"

		init_method = "| Initialization Method: "
		if self.random: init_method += "Random"
		else: init_method += "File: " + self.in_file_path
		output += init_method + "\n"

		output += "| Seed: " + str(self.seed_val) + "\n"
		if self.max_util: output += "| Max Util: " + str(self.max_util) + "\n"
		output += "+" + "-" * 60 													+ "\n"
		output += "| Total: " + str(round(adapt_proc_stats[3], 2)) + "(s)" 			+ "\n"
		output += "| CPU time: " + str(round(adapt_proc_stats[4], 2)) + "(s)"		+ "\n"
		output += "| Number of nodes: " + str(adapt_proc_stats[5])					+ "\n"
		output += "| Number of unique MGs: " + str(adapt_proc_stats[6])				+ "\n"
		output += "| Number of leaves: " + str(adapt_proc_stats[7])					+ "\n"
		output += "| Number of Unique Terminal Games: " + str(adapt_proc_stats[8])	+ "\n"
		output += "| Number of SMEs: " + str(adapt_proc_stats[9])					+ "\n"
		
		## Knowledge percentage
		max_know, max_know_id = self.adapt_proc.get_max_knowledge()
		output += "| Max Knowledge Percentage: " + str(max_know) + "%"	+ "\n"
		output += "| MG with max knowledge: " + str(max_know_id)		+ "\n"
		
		output += "+" + 60 * "-" + "\n"
		if self.debug:
			debug_stats = self.debugging.get_stats()
			output += "| Total GAMBIT time: " + str(round(debug_stats[0], 2)) + "(s)" 										+ "\n"
			output += "| Number of GAMBIT calls: " + str(debug_stats[1])													+ "\n"
			output += "| Average time per GAMBIT call: " + str(round(debug_stats[2], 3)) + "(s)"							+ "\n"
			output += "| Total CLINGO time: " + str(round(debug_stats[3], 2)) + "(s)"										+ "\n"
			output += "| Number of CLINGO calls: " + str(debug_stats[4])													+ "\n"
			output += "| Average time per CLINGO call: " + str(round(debug_stats[5], 3)) + "(s)"							+ "\n"
			output += "+" + 60 * "-"																						+ "\n"
			output += "| GAMBIT time / Total Time %: " + str(round(debug_stats[0] / adapt_proc_stats[3] * 100, 2)) + "%"	+ "\n"
			output += "| CLINGO time / Total Time %: " + str(round(debug_stats[3] / adapt_proc_stats[3] * 100, 2)) + "%"	+ "\n"
			output += "| CPU time / Total Time %: " + str(round(adapt_proc_stats[4] / adapt_proc_stats[3] * 100, 2)) + "%"	+ "\n"
			output += "+" + 60 * "-"																						+ "\n"
			output += "| # Zeros Mixed Strategy: " + str(debug_stats[6])													+ "\n"
			output += "| # Mixed Strategies \w sum <= 1: " + str(debug_stats[7])											+ "\n"
			output += "| # No NE after GAMBIT call: " + str(debug_stats[8])													+ "\n"
			output += "| Too many threads: " + str(debug_stats[9])															+ "\n"
			output += "+" + 60 * "-"																						+ "\n"
		
		
		return output
		
	########
	# Exec #
	########
	def exec(self):
		assert self.adaptation_procedure_done == False
		
		## Print About
		if not (self.quiet or self.no_out): about.print_about()
		
		## Print Help
		if self.help:
			help.print_help()
			return
		
		## Print Root
		if self.root and not self.no_out:
			if not self.quiet: print(colored("\n\t## Root ##", "blue"))
			else: print("\n# Root",)
			self.adapt_proc.print_root()
		
		## Save Root
		if self.save_root:
			f = open(self.sav_root_path, "w")
			f.write(self.adapt_proc.root_export())
			f.close()
		
		## Execute the Adaptation Procedure
		self.adapt_proc.adaptation_procedure()
		self.adapt_proc.wait_for_results()
		self.adapt_proc.turn_off()
		self.adaptation_procedure_done = True
		
		## Print stable set
		if not self.no_out:
			if not self.quiet: print(colored("\n\t## Terminal Set ##", "blue"))
			else: print("\n# Terminal Set",)
			self.adapt_proc.print_stable_set()
		
		## Print stable misinformed equilibria
		if not self.no_out:
			if not self.quiet: print(colored("\n\t## Stable Misinformed Equilibria ##", "blue"))
			else: print("\n# Stable Misinformed Equilibria",)
			self.adapt_proc.print_smes()
		
		## Print Statistics
		if not (self.quiet or self.no_out):
			if not self.quiet: print(colored("\n\t## Statistics ##", "blue"))
			else: print("\n# Statistics",)
			self.print_stats()
		
		## Print Tree
		if self.tree and not self.no_out:
			if not self.quiet: print(colored("\n\t## Adaptation Tree ##", "blue"))
			else: print("\n# Tree",)
			self.adapt_proc.print_tree()
		
		## Save Tree
		if self.save_tree:
			f = open(self.sav_tree_path, "w")
			f.write(self.adapt_proc.str_tree())
			f.close()
		
		## Print leaves
		if self.leaves and not self.no_out:
			if not self.quiet: print(colored("\n\t## Leaves ##", "blue"))
			else: print("\n# Leaves",)
			self.adapt_proc.print_leaves()
		
		## Print Nodes
		if self.nodes and not self.no_out:
			if not self.quiet: print(colored("\n\t## Nodes ##", "blue"))
			else: print("\n# Nodes",)
			self.adapt_proc.print_nodes()
		
		## Print Uniq MGs
		if self.uniq_mgs and not self.no_out:
			if not self.quiet: print(colored("\n\t## MG Pool ##", "blue"))
			else: print("\n# MG Pool",)
			self.adapt_proc.print_mg_pool()
		
		## Export Unique MGs
		if self.sav_uniq_mgs:
			self.adapt_proc.export_mg_pool(self.uniq_mgs_dir)
		
		## Export the stable set .mg files
		if self.sav_stable_set:
			self.adapt_proc.export_terminal_set(self.st_set_dir)
	
	
	##########
	# Output #
	##########
	
	def get_root(self):
		assert self.adaptation_procedure_done == True
		return self.adapt_proc.root_export()
	
	def get_SMEs(self):
		assert  self.adaptation_procedure_done ==  True
		return self.adapt_proc.str_smes()
	
	def get_nodes(self):
		assert self.adaptation_procedure_done == True
		return self.adapt_proc.str_nodes()
	
	def get_tree(self):
		assert self.adaptation_procedure_done == True
		return self.adapt_proc.str_tree()
	
	def get_mg_pool(self):
		assert self.adaptation_procedure_done == True
		return self.adapt_proc.str_mg_pool()
	
	def get_num_uniq_mgs(self):
		assert self.adaptation_procedure_done == True
		return self.get_progress_computed_mgs()
	
	def get_uniq_mg_files(self):
		assert self.adaptation_procedure_done == True
		return self.adapt_proc.list_export_mg_pool()
		
