#####################################################################
# adaptation_procedure.py
# ------------------------------------------------------------------
# This module encodes the algorithm of the adaptation procedure. The
# "main" class AdaptationProcedure constructs the Adaptation Tree and
# computes the SMEs of a misinformation game.
#
# Examples:
#	1. Initialize from file:
#
#	| import adaptation_procedure as ap
#	|
#	| f = open("../input_data/2x2_mg_example.mg", r)
#	| file_fmt = f.read()
#	| f.close()
#	|
#	| adapt_proc = ap.AdaptationProcedure()
#	| adapt_proc.root_from_file(file_fmt)
#	|
#	| adapt_proc.adaptation_procedure()
#
#
#	2. Randomly initialize
#
#	| import adaptation_procedure as ap
#	|
#	| num_players = 2
#	| strategies = 2
#	| max_util = 10
#	|
#	| adapt_proc = ap.AdaptationProcedure()
#	| adapt_proc.root_random(num_players, strategies, max_util)
#	|
#	| adapt_proc.adaptation_procedure()
#
# The method adaptation_procedure takes two boolean arguments, quiet,
# and fast_mode. By default, both of them are False. The quiet argument
# regards some output messages. For distinction between "slow" and "fast"
# mode see the SETN 2022 submitted paper (included in the projects directory).
# The *fast* mode is recommended, while it implements an elaborate algorithm.
# The slow mode, is the *naive* approach.
#
# To use the fast mode replace the call to the adaptation_procedure() method
# with the following:
#
#	| quiet = False
#	| fast_mode = True
#	| adapt_proc.adaptation_procedure(quiet, fast_mode)
#
#
# Classes:
#
#	1) AdaptationNode:		Implements a node of the Adaptation Procedure.
#							Contains a "pointer" to a misinformation game.
#							Because a MG may appear multiple times in a
#							procedure, we keep a pointer, in order to avoid
#							unnecessary computations.
#
#	2) AdaptationProcedure:	Implements the Algorithm of the Adaptation
#							Procedure, which is a variant of the BFS.
#							Also, has a dictionary, mg_pool as a data
#							member. This dictionary corresponds the
#							sets of position vectors that have been
#							updated in a misinformation game to a
#							misinformation game. The class AdaptationNode
#							contains labels to the key values of this
#							structure.
#
# author: Merkouris Papamichail
# email: mercoyris@ics.forth.gr
# institute: ICS, FORTH
# last update: 25/10/2022
#####################################################################

#############
# Libraries #
#############

# custom libraries
from misinformation_game import MisinformationGame
import clingo
import gambit
import auxiliary_functions as ax

# python libraries
import itertools	# itertools.product for preprocessing
import re  			# regex
import math  		# prod
import time  		# process_time
import sys
from os import path	# is dir
import pprint
import threading

# 3rd party libraries
# NOTE: Simple, lightweight and extensible Tree data structure.
# See Doc: https://anytree.readthedocs.io/en/latest/
from anytree import NodeMixin, RenderTree

#############
# Constants #
#############

changed_clingo_predicate = "changed"
unchanged_clingo_predicate = "unchanged"



####################
# Helper Functions #
####################

## Preprocessing
###########################################################
# This function establishes the a priori knowledge of
# the agents in an MG. Namely, the position vectors, of
# some MG, such that, when applied the update operation
# on MG at the position designated by pos_vec, no change
# occurs.
###########################################################
def preprocess_mg(mg, strategies):
	num_players = len(strategies)

	unique_key = []
	for pos_vec in itertools.product(*[strategies] * num_players):
		clingo_pos_vec = ax.pos_vec2clingo(pos_vec)
		answer_set = clingo.addaptation_step(mg.get_clingo_format(), clingo_pos_vec)

		if unchanged_clingo_predicate in answer_set:
			unique_key.append(pos_vec)

	return ax.path_to_set(unique_key)

###########
# Classes #
###########

class AdaptationNode(NodeMixin):

	def __init__(self, node_id, nme_path, unique_key, MG, parent=None, changed_from_parent=True, new_mg=True):
		assert MG != None

		# some bookkeeping
		self.node_id = node_id

		# initialize anytree node
		NodeMixin.__init__(self)
		self.parent = parent  # set parent, if any
		self.name = "N_" + node_id + ", MG_" + MG.get_game_id() + ", (" + str(MG.get_knowledge_percentage()) + "%)" # set name to be printed, when
		# we render the tree

		# "pointer" to a misinformation game
		self.misinformation_game = MG

		# We keep the path of NMEs that got us to
		# this node in the adaptation tree, starting
		# from the root.
		self.nme_path = nme_path

		# We create a set from the path of NMEs.
		# We encode the set as tuple, i.e.
		# we delete duplicates and sort.
		# The unique key is the "key" of the
		# mis_game_pool dictionary
		# (see below class AdaptationProcedure)
		self.unique_key = unique_key

		## State
		# We keep a boolean variable, that's true
		# iff this node is different from it's
		# parent.
		# By default the root is different.
		self.changed_from_parent = changed_from_parent

		# is a new MG, by default the root is
		self.new_mg = new_mg

	##########
	# String #
	##########

	def __str__(self):
		hline = "-" * 40
		return "| Node Name: " + self.name + "\n" \
			   + "| Unique MG id: " + str(self.misinformation_game.game_id) + "\n" \
			   + "| Previous NMEs Path: " + str(self.nme_path) + "\n" \
			   + "| Unique Key: " + str(self.unique_key) + "\n" \
			   + "| NMEs: " + str(self.misinformation_game.nme.keys()) + "\n"

	#############
	# Accessors #
	#############

	def is_changed_from_father(self):
		return self.changed_from_parent

	def is_new_mg(self):
		return self.new_mg

	def get_node_id(self):
		return self.node_id

	def get_mg_id(self):
		return self.misinformation_game.get_game_id()

	def get_mg_pointer(self):
		return self.misinformation_game

	def get_nme_path(self):
		return self.nme_path

	def get_unique_key(self):
		return self.unique_key

	def get_num_players(self):
		return self.misinformation_game.get_num_players()

	def get_strategies(self):
		return self.misinformation_game.get_strategies()

	def get_clingo_description(self):
		return self.misinformation_game.get_clingo_format()

	def get_num_nmes(self):
		return self.misinformation_game.get_num_nmes()

	def get_nmes(self):
		return self.misinformation_game.get_nme_list()

	def get_nme_dict(self):
		return self.misinformation_game.get_nme_dict()

	def get_clingo_nme_dict(self):
		return self.misinformation_game.get_nme_clingo()

	def insert_sme(self, sme):
		self.misinformation_game.insert_sme(sme)


#####################################################################
# Class AdaptationProcedure
# ------------------------------------------------------------------
# Data Members:
#	1. mis_game_pool:	A dictionary of the form
#							dict: (nme_1, ...,nme_k) --> MG
#						Observe that the nmes are strategy profiles,
#						i.e.: positions in the original game. We keep
#						the positions that changed from the original
#						game.
#						We force the tuple of tuples (nme_1, ...,nme_k)
#						to be a set, i.e. no duplicates.
#
#####################################################################
class AdaptationProcedure:

	##################
	# Initialization #
	##################

	def __init__(
			self,
			gambit_pac,
			debugging,
			domain,
			num_mult_threads_traversal = 4,
			quiet = False,
			fast_mode = False
	):

		# Prelimineries: Fast mode
		self.fast_mode_on = fast_mode

		# Prelimineries: Quiet
		self.quiet = quiet

		# Prelimineries: GAMBIT
		self.gambit_pac = gambit_pac

		# Prelimineries: Debugging
		self.debugging = debugging

		# Prelimineries: Domain
		self.domain = domain
		

		## A pool of Misinformation Games
		self.mis_game_pool = dict()
		self.uniq_mg_counter = 0
		## Lock for mg_pool
		self.mis_game_pool_lock = threading.Lock()


		## Initial set of nodes
		self.queue = []
		## Lock for queue
		self.queue_lock		= threading.Lock()
		self.queue_empty	= threading.Condition(self.queue_lock)

		## List of leaves
		self.leaves = []
		## Lock for leaves
		self.leaves_lock = threading.Lock()

		## Terminal Set,
		## set of the stable games
		self.terminal_set = set()
		## Lock for Terminal Set
		self.terminal_set_lock = threading.Lock()

		## Stable misinformed equilibria
		self.smes = set()
		## Lock for SMEs
		self.smes_lock = threading.Lock()

		# the root of the adaptation procedure
		# initialized to None at the beginning
		self.root = None

		## We keep a list of the nodes
		self.node_list = []
		## Node List Lock
		self.node_list_lock = threading.Lock()

		## Statistics
		self.cpu_time	= time.process_time()  # CPU time (not including GAMBIT or CLINGO)
		self.total_time = time.time()  # total time (including the subprocesses)
		self.max_knowledge_percentage = None
		self.max_knowledge_percentage_mg_id = None



		# states
		self.root_initialized = False
		self.adaptation_procedure_completed = False

		##################
		# Multithreading #
		##################
		self.tasks			= 0
		self.tasks_lock		= threading.Lock()
		self.pending_tasks	= threading.Condition(self.tasks_lock)

		self.traversal_threading_operation_on = True
		self.num_mult_threads_traversal = num_mult_threads_traversal

		assert num_mult_threads_traversal >= 1
		self.workers = []
		for i in range(num_mult_threads_traversal):
			self.workers.append(threading.Thread(target=self.traversal_thread_operate))

	
	##################
	# Multithreading #
	##################
	
	def traversal_thread_operate(self):

		while self.traversal_threading_operation_on:

			###########################
			# Acquire Adaptation Node #
			###########################


			## Acquire the lock
			self.queue_lock.acquire()


			## If the queue is empty, wait
			while self.queue == [] and self.traversal_threading_operation_on:
				self.tasks_lock.acquire()
				self.pending_tasks.notify_all()
				self.tasks_lock.release()

				self.queue_empty.wait()

			## If you woke from waiting, with an empty queue return
			if self.queue == [] and not self.traversal_threading_operation_on:
				self.queue_lock.release()
				return

			## Get an Adaptation Node from the queue
			parent = self.queue.pop()


			## Release the lock
			self.queue_lock.release()


			#########################
			# Do an Adaptation Step #
			#########################

			self._adaptation_step(parent)

			if not self.quiet:
				print("# Progress Uniq MGs: " + str(self.uniq_mg_counter) + "/" + str(self.max_it), end="\r")

			#############################
			# Decrease the task counter #
			#############################
			self.tasks_lock.acquire()

			assert self.tasks > 0
			self.tasks -= 1

			if self.tasks == 0: self.pending_tasks.notify_all()

			self.tasks_lock.release()

	def wait_for_results(self):

		self.tasks_lock.acquire()
		while self.tasks > 0:
			self.pending_tasks.wait()
		self.tasks_lock.release()
		
		self.adaptation_procedure_completed = True


	def turn_off(self):

		self.traversal_threading_operation_on = False

		self.queue_lock.acquire()
		self.queue_empty.notify_all()
		self.queue_lock.release()

		total_end_t = time.time()
		cpu_end_t = time.process_time()
		self.total_time = total_end_t - self.total_time
		self.cpu_time = cpu_end_t - self.cpu_time

	
	def __del__(self):
		for i in range(self.num_mult_threads_traversal):
			self.workers[i].join()

	

	##############################
	# Print & String Convertions #
	##############################

	def print_smes(self):
		assert self.adaptation_procedure_completed == True

		pprint.pprint(self.smes)
	
	def str_smes(self):
		assert self.adaptation_procedure_completed == True
		return pprint.pformat(self.smes)

	def print_tree(self):
		assert self.adaptation_procedure_completed == True

		for pre, _, node in RenderTree(self.root):
			print("%s%s" % (pre, node.name))

	def str_tree(self):
		assert self.adaptation_procedure_completed == True

		output = ""
		for pre, _, node in RenderTree(self.root):
			output += "%s%s" % (pre, node.name) + "\n"

		return output

	def print_root(self):

		print(self.root.misinformation_game.export())
		print("\n")

	def root_export(self):
		return self.root.misinformation_game.export()

	def print_nodes(self):
		assert self.adaptation_procedure_completed == True

		for node in self.node_list:
			print(node)
	
	def str_nodes(self):
		assert self.adaptation_procedure_completed == True
		
		output = ""
		for node in self.node_list: output += str(node) + "\n"
		
		return output
	

	def print_leaves(self):
		assert self.adaptation_procedure_completed == True

		for leaf in self.leaves:
			print(leaf)

	def print_stable_set(self):
		assert self.adaptation_procedure_completed == True

		for s in self.terminal_set:
			print("MG_" + self.mis_game_pool[s].get_game_id() + ": " + str(s))

	def print_mg_pool(self):
		assert self.adaptation_procedure_completed == True

		for key in self.mis_game_pool.keys():
			print(self.mis_game_pool[key])
			print("| Unique Key: " + str(key) + "\n")
	
	def str_mg_pool(self):
		assert self.adaptation_procedure_completed == True
		
		output = ""
		for key in self.mis_game_pool.keys():
			output += str(self.mis_game_pool[key])
			output += "| Unique Key: " + str(key) + "\n"
		
		return output

	# Given a path to directory
	# saves each unique MG as a .mg file
	# under the given directory.
	def export_mg_pool(self, mg_dir_path):
		assert self.adaptation_procedure_completed == True
		assert path.isdir(mg_dir_path)

		## this line will cause trouble in Windows
		if mg_dir_path[-1] != "/": mg_dir_path += "/"

		for MG in self.mis_game_pool.values():
			mg_file_path = mg_dir_path + "uniq_mg" + MG.get_game_id() + ".mg"
			f = open(mg_file_path, "w")
			f.write(MG.export())
			f.close()

	# Return a loong string of all unique MG files
	# useful for jupyter notebook and presentation
	# purposes
	def str_export_mg_pool(self):
		assert self.adaptation_procedure_completed == True
		output = ""

		for MG in self.mis_game_pool.values():
			output += MG.export()
			output += "\n\n"

		return output
	
	def list_export_mg_pool(self):
		assert self.adaptation_procedure_completed == True
		
		output = []
		for MG in self.mis_game_pool.values(): output.append(MG.export() + "\n\n")
		
		return output

	def str_export_mg_by_key(self, unique_key):
		assert self.adaptation_procedure_completed == True
		assert unique_key in self.mis_game_pool.keys()

		return self.mis_game_pool[unique_key].export()

	# Given a path to directory
	# saves each unique MG as a .mg file
	# under the given directory.
	def export_terminal_set(self, ss_dir_path):
		assert self.adaptation_procedure_completed == True
		assert path.isdir(ss_dir_path)

		## this line will cause trouble in Windows
		if ss_dir_path[-1] != "/": ss_dir_path += "/"

		for unique_key in self.terminal_set:
			MG = self.mis_game_pool[unique_key]
			ss_file_path = ss_dir_path + "stable_mg" + MG.get_game_id() + ".mg"
			f = open(ss_file_path, "w")
			f.write("# Unique Key: " + str(unique_key) + "\n")
			f.write(MG.export())
			f.close()

	# Return a loong string of all stable MG files
	# useful for jupyter notebook and presentation
	# purposes
	def str_export_terminal_set(self):
		assert self.adaptation_procedure_completed == True
		output = ""

		for unique_key in self.terminal_set:
			MG = self.mis_game_pool[unique_key]
			output += "# Unique Key: " + str(unique_key) + "\n"
			output += MG.export()
			output += "\n\n"

		return output

	def print_stats(self):
		assert self.adaptation_procedure_completed == True

		print("+" + 39 * "-")
		print("| Number of players: " + str(self.root.get_num_players()))
		print("| Strategies Vector: " + str(self.root.get_strategies()))

		print("+" + "-" * 39)
		print("| NE Method: " + self.gambit_pac.get_default_method_name())
		print("| Total: " + str(self.total_time) + "(s)")
		print("| CPU time: " + str(self.cpu_time) + "(s)")
		print("| Number of nodes: " + str(len(self.node_list)))
		print("| Number of unique MGs: " + str(len(self.mis_game_pool.items())))
		print("| Number of leaves: " + str(len(self.leaves)))
		print("| Number of Unique Terminal Games: " + str(len(self.terminal_set)))
		print("| Number of SMEs: " + str(len(self.smes)))
		print("+" + 39 * "-")

	#############
	# Accessors #
	#############
	
	def get_is_adaptation_concluded(self):
		return self.adaptation_procedure_completed
	
	def get_total_mgs(self):
		return self.max_it
	
	def get_progress_computed_mgs(self):
		return self.uniq_mg_counter

	def get_num_players(self):
		assert self.root_initialized == True

		return self.root.get_num_players()

	def get_strategies(self):
		assert self.root_initialized == True

		return self.root.get_strategies()

	def get_stats(self):
		assert self.adaptation_procedure_completed == True

		return [self.root.get_num_players(),  # number of players
				# math.prod(self.root.get_strategies()),		# number of strategy profiles
				self.root.get_strategies(),
				self.gambit_pac.get_default_method_name(),  # Method's Name
				self.total_time,  # total time
				self.cpu_time,  # cpu time
				len(self.node_list),  # number of nodes
				len(self.mis_game_pool.items()),  # number of unique misinformation games
				len(self.leaves),  # number of leaves
				len(self.terminal_set),  # number of terminal set, aka stable set, aka uniq leaf mis. games
				len(self.smes)]  # number of smes
	
	def get_max_knowledge(self):
		if self.max_knowledge_percentage is None:
			self.find_gretest_knowledge()
		
		return self.max_knowledge_percentage, self.max_knowledge_percentage_mg_id

	##############
	# Predicates #
	##############

	def mg_already_computed(self, new_unique_key):
		self.mis_game_pool_lock.acquire()
		is_already_computed = new_unique_key in self.mis_game_pool.keys()

		## If the MG is NOT already computed, then *this* thread will
		## proceed to compute the new MG. Therefore, the lock will
		## be released in _new_mis_game() method. (See also, the related
		## comment there).
		if is_already_computed: self.mis_game_pool_lock.release()

		return is_already_computed

	###########
	# Methods #
	###########
	## Generate Root form File
	def root_from_file(self, file_fmt):
		assert self.root_initialized == False

		######################
		# Filter the results #
		######################
		lines = file_fmt.split("\n")  # Split the file in lines.

		lines = list(filter(lambda line: line != "", lines))  # Discard the empty lines, if any.
		lines = list(
			filter(lambda line: re.search("^#", line) == None, lines))  # Discard comment lines starting with "#".

		#####################
		# Retrieve the info #
		#####################
		num_players = int(ax.head(lines))  # The first line should be the number of players.
		strat_tokens = ax.head(lines).split(" ")  # Split tokens
		strat_tokens = list(filter(lambda line: line != "", strat_tokens))  # Discard empty tokens
		strategies = list(map(int, strat_tokens))  # The 2nd line describes the strategies vector.

		## check the GAMBIT method
		# Check whether the designated method supports num_player-player games
		assert num_players <= gambit.method_max_players_list[self.gambit_pac.get_default_method_val()], \
			"Error: The designated NE computation method does NOT support " + str(num_players) + "-player games!"

		#####################
		# Initialise Domain #
		#####################
		self.domain.initialise(num_players, strategies)


		#####################
		# Initialize the MG #
		#####################
		MG = MisinformationGame(self.gambit_pac, self.debugging, self.domain,
								str(self.uniq_mg_counter), num_players,
								strategies)  # Initialize the MG, num_players & strategies vector.
		self.uniq_mg_counter += 1

		num_SPs = math.prod(strategies)  # Compute the number of the stratetgy profiles.

		for player in range(0, MG.get_num_players() + 1):  # Pass the related lines to the NFG of he root MG.
			MG.games[player].utilities_from_str(
				lines[
				player * num_SPs:
				player * num_SPs + num_SPs
				]
			)

		MG.utilities_generated = True  # Update MG's state.

		MG.compute_nme_dict()  		# Compute the nmes (calls GAMBIT).
		MG.compute_pos_vecs()  		# From dictionary to list of tuples.
		MG.clingo_compile_format()  # Compute the description of the game in clingo format.
		MG.clingo_compile_nme()  	# Compile a list of clingo-predicates describing the nmes
		
		## Compute Knoweledge
		answer_set = clingo.addaptation_step(MG.get_clingo_format(), "")
		MG.compute_knowledge_from_answer_set(answer_set)

		##############################
		# Initialize Adaptation Node #
		##############################
		unique_key = preprocess_mg(MG, MG.get_strategies())
		self.root = AdaptationNode("0", list(unique_key), unique_key, MG)  # Create an Addaptation Tree Node and make it point
		# to the new MG.
		self.root_initialized = True  # Update state.

		##############################
		# Initialize Data Structures #
		##############################
		self.mis_game_pool[self.root.get_unique_key()] = MG  # The root will always be added to the dictionary.

		self.queue.append(self.root)  # Insert node to queue.

		self.node_list.append(self.root)  # Insert to node list.

		self.tasks += 1





	## Generate Root Randomly
	def root_random(self, num_players, strategies, max_utility):
		assert self.root_initialized == False

		## check the GAMBIT method
		# Check whether the designated method supports num_player-player games
		assert num_players <= gambit.method_max_players_list[self.gambit_pac.get_default_method_val()], \
			"Error: The designated NE computation method does NOT support " + str(num_players) + "-player games!"

		#####################
		# Initialise Domain #
		#####################
		self.domain.initialise(num_players, strategies)

		#####################
		# Initialize the MG #
		#####################
		MG = MisinformationGame(self.gambit_pac, self.debugging, self.domain,
								str(self.uniq_mg_counter), num_players,
								strategies)  # Initialize the MG, num_players & strategies vector.
		self.uniq_mg_counter += 1

		MG.generate_random_utilities(max_utility)  # Generate Utilities

		MG.compute_nme_dict()  # Compute the nmes (calls GAMBIT).
		MG.compute_pos_vecs()  # From dictionary to list of tuples.
		MG.clingo_compile_format()  # Compute the description of the game in clingo format.
		MG.clingo_compile_nme()  # Compile a list of clingo-predicates describing the nmes
		
		## Compute Knoweledge
		answer_set = clingo.addaptation_step(MG.get_clingo_format(), "")
		MG.compute_knowledge_from_answer_set(answer_set)
		
		
		##############################
		# Initialize Adaptation Node #
		##############################
		## Preprocessing
		unique_key = preprocess_mg(MG, MG.get_strategies())
		self.root = AdaptationNode("0", list(unique_key), unique_key, MG)  # Create an Addaptation Tree Node and make it point
		# to the new MG.
		self.root_initialized = True  # Update state.

		##############################
		# Initialize Data Structures #
		##############################
		self.mis_game_pool[self.root.get_unique_key()] = MG  # The root will always be added to the dictionary.

		self.queue.append(self.root)  # Insert node to queue.


		self.node_list.append(self.root)  # Insert to node list.

		self.tasks += 1




	########################
	# Adaptation Procedure #
	########################


	###############################################################
	# adaptation_step()
	# ------------------------------------------------------------
	# This method handles the already computed Adaptation Node.
	# If the node "points" to the same MG as it's parent, then:
	# 	a) we stop the procedure for this node,
	#	b) try to add it to the stable set
	# Else:
	#	a) we append the child to the Queue
	#	b) and continue the adapt. proc. for the child node.
	###############################################################
	def _adaptation_step(self, parent):

		## get the dictionary of nmes to pos vectors
		nmes_dict = parent.get_nme_dict()  # A dictionary from the NMEs to the derived pos_vecs
		clingo_nme_dict = parent.get_clingo_nme_dict()  # A dictionary from the NMEs to the *prerdices* of
		# the derived pos_vecs

		# Id counter
		i = 1

		###################
		# Create Requests #
		###################
		#######################################################################
		# The 1st phase of the adaptation step.
		# In this step we create queries of the form:
		#	(
		#		request_parent,		# a pointer to the parent node
		#		request_nme,		# the NME as tuple of real numbers
		#		tuple_pos_vec,		# a pos. vec. corresponding to the NME,
		#							# as tuple of integers
		#		pred_pos_vec		# the pos. vec. as a clingo predicate
		#	)
		# We use these requests to check wheather the resulting MG, when the
		# update operation is applied, is a) different of its parent and b)
		# to compute the new MG.
		#######################################################################

		Requests = []
		visited_pos_vecs = set()					# 2 NMEs may have the same pos. vecs.
													# therefore, we keep a set of the already
													# considered pose vecs.
		for nme in nmes_dict.keys():
			for pos in range(len(nmes_dict[nme])):

				request_parent  = parent						# a pointer to the parent node
				request_nme     = nme							# the NME as tuple of real numbers
				tuple_pos_vec   = nmes_dict[nme][pos]			# one of the position vectors corresponding
                                                                # to the NME
				pred_pos_vec    = clingo_nme_dict[nme][pos]	    # the pos. vec. as CLINGO predicate
				
                ## Compute the changed_from_parent bit
				parents_path        = request_parent.get_nme_path()
				changed_from_parent = not tuple_pos_vec in parents_path


				if tuple_pos_vec in visited_pos_vecs:		# if we considered the pos. vec. in a previous
					continue								# NME, continue
				else:
					visited_pos_vecs.add(tuple_pos_vec)


				request_tuple = tuple([request_parent, request_nme, tuple_pos_vec, pred_pos_vec, changed_from_parent])
				Requests.append(request_tuple)

		##################
		# Handle Results #
		##################
		## Do the Adaptation (sub) Step
		for result_tuple in Requests:

			## ceate node id
			new_node_id = parent.get_node_id() + str(i)
			i += 1

			## call adaptation_substep()
			child = self._adaptation_substep(new_node_id, parent, result_tuple[2], result_tuple[4], result_tuple[3])

			## Append to node list
			self.node_list_lock.acquire()
			self.node_list.append(child)
			self.node_list_lock.release()


			## If the child did not change from father
			## then it is a leaf (and belongs to the terminal set)!
			if not child.is_changed_from_father():

				## Append to Leaves
				self.leaves_lock.acquire()
				self.leaves.append(child)
				self.leaves_lock.release()

				## Add to terminal Set
				self.terminal_set_lock.acquire()
				self.terminal_set.add(child.get_unique_key())
				self.terminal_set_lock.release()

				## Continue
				continue


			## If fast_mode == True, and we have encounter the child
			## on another branch, do not add the node in the queue
			if self.fast_mode_on and not child.is_new_mg(): continue


			## If non of the above holds, add the new child to the queue,
			## to explore this branch further.
			# Acquire lock
			self.queue_lock.acquire()

			# Append to queuue
			self.queue.append(child)  ## BFS
			# self.queue.insert(0, child)			## uncomments this for DFS
													## (no visible change in time consumption for DFS)

			## Tasks counter
			self.tasks_lock.acquire()
			self.tasks += 1
			self.tasks_lock.release()


			# Wake the theads that wait the condition vaiable
			self.queue_empty.notify_all()

			# Rrelease the lock
			self.queue_lock.release()



		################
		# Compute SMEs #
		################

		not_changed_pos_vecs = set()
		for result_tuple in Requests:
			if not result_tuple[4]:  not_changed_pos_vecs.add(result_tuple[2])

		for nme in nmes_dict.keys():
			is_sme = True
			for pos in range(len(nmes_dict[nme])):
				is_sme = is_sme and nmes_dict[nme][pos] in not_changed_pos_vecs

			## If is_sme, add to SMEs
			if is_sme:
				self.smes_lock.acquire()
				self.smes.add(nme)
				self.smes_lock.release()



	###############################################################
	# adaptation_substep()
	# ------------------------------------------------------------
	# This method returns a valid AdaptationNode, given it's parent
	# and a NME.
	# We have the following 4 cases:
	#
	#	1. 	NME in parent's NMEs path, then the child *is* its
	#		parent. Observe that the opposite direction does not
	#		hold.
	#
	#	2. 	The 1st does not hold. We need to call clingo to
	#		decipher. Check weather the predicate unchanged/0 is in
	#		the answer set. If it is, then also the node "points"
	#		to its parent.
	#
	# The (1), (2) will conclude in stopping the procedure for this
	# branch. The following cases will allow the adapt. proc. to
	# continue for this branch. But it is possible we have already
	# computed the child MG in another branch.
	#
	# Check if child's unique key is already in
	# self.mis_game_pool.keys().
	#	3.	If, true, make the child point to the
	#		self.mis_game_pool[unique_key]
	#
	#	4. Else, create a new MG.
	#
	###############################################################
	def _adaptation_substep(self, node_id, parent, tuple_pos_vec, changed_from_parent, pred_pos_vec):
		parents_path = parent.get_nme_path()
		parents_unique_key = parent.get_unique_key()
		new_path = parents_path + [tuple_pos_vec]
		new_unique_key = ax.path_to_set(new_path)

		# (Old) Case 1 & 2
		if not changed_from_parent:
			parents_MG = parent.get_mg_pointer()
			return AdaptationNode(node_id, new_path, parents_unique_key, parents_MG, parent, False, False)

		# Case 3
		if self.mg_already_computed(new_unique_key):
			MG = self.mis_game_pool[new_unique_key]
			return AdaptationNode(node_id, new_path, new_unique_key, MG, parent, True, False)

		# Case 4
		new_MG = self._new_mis_game(parent, new_unique_key, pred_pos_vec)
		return AdaptationNode(node_id, new_path, new_unique_key, new_MG, parent, True, True)



	#####################################################
	# Input:
	#	1. parent:		Adaptation Node
	#	2. clingo_nme:	A clingo predicate describing
	#					the nme
	#
	# Action:
	#	* Adding a new MG to the pool
	#
	# Output:
	#	* A pointer to the MG created
	#####################################################
	def _new_mis_game(self, parent, new_unique_key, pred_pos_vec):

		## compute the uniq id for the MG
		mg_uniq_id = str(self.uniq_mg_counter)
		self.uniq_mg_counter += 1

		## get the number of players
		mg_num_players = parent.get_num_players()

		## get the strategies vector
		mg_strategies = parent.get_strategies()

		## create the Misinformation Game
		MG = MisinformationGame(
			self.gambit_pac,
			self.debugging,
			self.domain,
			mg_uniq_id,
			mg_num_players,
			mg_strategies
		)

		## add the new MG to the pool
		self.mis_game_pool[new_unique_key] = MG
		## Release the lock, acquired in mg_alerady_computed()
		## This way we achieve a) no (considerable) waiting time,
		## b) no redundant calculations.
		self.mis_game_pool_lock.release()

		## compute utilities from clingo
		parent_mg = parent.get_mg_pointer()

		clingo_call_start_t = time.time()
		answer_set = clingo.addaptation_step(parent_mg.get_clingo_format(), pred_pos_vec)
		clingo_call_end_t = time.time()
		self.debugging.clingo_call(clingo_call_end_t - clingo_call_start_t)

		MG.utilities_from_clingo(answer_set)

		## we compute everything beforehand
		## compute nmes
		MG.compute_nme_dict()
		MG.compute_pos_vecs()

		## compute clingo description etc.
		MG.clingo_compile_format()
		MG.clingo_compile_nme()


		## return the new nme path set
		return MG
	
	def find_gretest_knowledge(self):
		assert self.adaptation_procedure_completed == True
		mg_pool_list = list(self.mis_game_pool.values())
		mg_pool_list.sort(key=lambda MG1: MG1.get_knowledge_percentage())
		
		self.max_knowledge_percentage 		= mg_pool_list[-1].get_knowledge_percentage()
		self.max_knowledge_percentage_mg_id	= mg_pool_list[-1].get_game_id()
	
	## Adaptation Procedure
	def adaptation_procedure(self):
		assert self.adaptation_procedure_completed == False
		assert self.root_initialized == True

		self.max_it = math.prod(self.root.get_strategies())
		self.max_it = 2 ** self.max_it

		total_start_t = time.time()
		cpu_start_t = time.process_time()

		for i in range(self.num_mult_threads_traversal): self.workers[i].start()

