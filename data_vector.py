import os
import os.path as path

class DataVector:
	
	##################
	# Initialization #
	##################
	
	def __init__(self):
		## Data
		self.root_file			= ""		# a .mg root file (String)
		self.smes				= ""		# a String containing the SMEs
		self.statistics			= ""		# a String containig statistics
		self.node_list			= ""		# a String containing a catalog of the nodes
		self.tree				= ""		# a String containig a figure of the adaptation tree
		self.mis_games_list		= ""		# a String containing a catalog of the unique misinformation games
		self.num_unique_mgs		= ""		# an Integer denoting the number of unique MGs
		self.uniq_mg_files		= []		# List of the .mg files representing the unique MGs
		
		
		## States
		self.root_file_set		= False
		self.smes_set			= False
		self.statistics_set		= False
		self.node_list_set		= False
		self.tree_set			= False
		self.mis_games_list_set	= False
		self.num_unique_mgs_set	= False
		self.uniq_mg_files_set	= False
	
	
	
	#########
	# Reset #
	#########
	
	def reset(self):
		## Data
		self.root_file 		= ""  # a .mg root file (String)
		self.smes 			= ""  # a String containing the SMEs
		self.statistics 	= ""  # a String containig statistics
		self.node_list 		= ""  # a String containing a catalog of the nodes
		self.tree 			= ""  # a String containig a figure of the adaptation tree
		self.mis_games_list = ""  # a String containing a catalog of the unique misinformation games
		self.num_unique_mgs = ""  # an Integer denoting the number of unique MGs
		self.uniq_mg_files 	= ""  # List of the .mg files representing the unique MGs
		
		## States
		self.root_file_set 		= False
		self.smes_set 			= False
		self.statistics_set 	= False
		self.node_list_set 		= False
		self.tree_set 			= False
		self.mis_games_list_set = False
		self.num_unique_mgs_set = False
		self.uniq_mg_files_set 	= False
	
	##############
	# Predicates #
	##############
	
	def is_empty(self):
		return self.root_file_set 	== False and\
			self.smes_set 			== False and\
			self.statistics_set 	== False and\
			self.node_list_set		== False and\
			self.tree_set			== False and\
			self.mis_games_list_set	== False and\
			self.num_unique_mgs_set	== False and\
			self.uniq_mg_files_set	== False
	
	
	########
	# Save #
	########
	
	def save_root_file(self, filename="root.mg"):
		f = open(filename, "w")
		f.write(self.root_file)
		f.close()
	
	def save_smes(self, filename="smes.txt"):
		f = open(filename, "w")
		f.write(self.smes)
		f.close()
	
	def save_statistics(self, filename="statistics.txt"):
		f = open(filename, "w")
		f.write(self.statistics)
		f.close()
	
	def save_node_list(self, filename="node_list.txt"):
		f = open(filename, "w")
		f.write(self.node_list)
		f.close()
	
	def save_tree(self, filename="tree.txt"):
		f = open(filename, "w")
		f.write(self.tree)
		f.close()
	
	def save_mis_game_list(self, filename="mg_list.txt"):
		f = open(filename, "w")
		f.write(self.mis_games_list)
		f.close()
	
	def export_mg_files(self, directory="unique_mg_files"):
		if not path.isdir(directory):
			os.mkdir(directory)
		
		## this line will cause trouble in Windows
		if directory[-1] != "/": directory += "/"
		
		
		for i in range(len(self.uniq_mg_files)):
			mg_file_path = directory + "uniq_mg_" + str(i) + ".mg"
			f = open(mg_file_path, "w")
			f.write(self.uniq_mg_files[i])
			f.close()
	
	
	def save_all(self, directory="adapt_proc_data"):
		## this line will cause trouble in Windows
		if directory[-1] != "/": directory += "/"
		
		# Save the Root
		root_file = directory + "root.mg"
		self.save_root_file(root_file)
		
		# Save the SMEs
		smes_file = directory + "smes.txt"
		self.save_smes(smes_file)
		
		# Save the Statistics
		stats_file = directory + "statistics.txt"
		self.save_statistics(stats_file)
		
		# Save the Node List
		nodes_list_file = directory + "node_list.txt"
		self.save_node_list(nodes_list_file)
		
		# Save Tree
		tree_file = directory + "tree.txt"
		self.save_tree(tree_file)
		
		# Save Mis. Game List
		mis_game_list_file = directory + "mis_games_list.txt"
		self.save_mis_game_list(mis_game_list_file)
		
		# Export Unique Misinformation Games
		uniq_mgs_dir = directory + "unique_mgs"
		self.export_mg_files(uniq_mgs_dir)
		
		
	
	
	#############
	# Accessors #
	#############
	
	def get_root_file(self):
		return self.root_file
	
	def get_smes(self):
		return self.smes
	
	def get_statistics(self):
		return self.statistics
	
	def get_node_list(self):
		return self.node_list
	
	def get_tree(self):
		return self.tree
	
	def get_mis_game_list(self):
		return self.mis_games_list
	
	def get_num_uniue_mgs(self):
		return self.num_unique_mgs
	
	def get_uniq_mg_files(self):
		return self.uniq_mg_files
	
	
	############
	# Mutators #
	############
	
	def set_root_file(self, root_file):
		assert self.root_file_set == False
		
		self.root_file		= root_file
		self.root_file_set	= True
	
	def set_smes(self, smes):
		assert  self.smes_set == False
		
		self.smes 		= smes
		self.smes_set	= True
	
	def set_statistics(self, stats):
		assert self.statistics_set == False
		
		self.statistics 	= stats
		self.statistics_set	= True
	
	def set_node_list(self, node_list):
		assert self.node_list_set == False
		
		self.node_list		= node_list
		self.node_list_set	= True
	
	def set_tree(self, tree):
		assert self.tree_set == False
		
		self.tree		= tree
		self.tree_set	= True
	
	def set_mis_game_list(self, mis_game_list):
		assert self.mis_games_list_set == False
		
		self.mis_games_list		= mis_game_list
		self.mis_games_list_set	= True
	
	def set_num_unique_mgs(self, num_uniq_mgs):
		assert self.num_unique_mgs_set == False
		
		self.num_unique_mgs		= num_uniq_mgs
		self.num_unique_mgs_set	= True
	
	def set_uniq_mg_files(self, uniq_mg_files):
		assert self.uniq_mg_files_set == False
		
		self.uniq_mg_files		= uniq_mg_files
		self.uniq_mg_files_set	= True
	
		
		