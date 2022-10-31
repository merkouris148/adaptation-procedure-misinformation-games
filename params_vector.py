#############
# Libraries #
#############

## Custom libraries
import application

## Python libraries
import os


##########################################
# Adaptation Procedure Parameters Vector #
##########################################

default_number_threads = 4
default_number_decimal_digits = 8


class init_method:
	file = 0
	random = 1


class ParamsVector:
	
	##################
	# Initialization #
	##################
	
	def __init__(self):
		# initialization method
		self.init_method = None
		self.init_from_file = None
		self.init_random = None
		
		# input file
		self.input_file = None
		
		# random parameters
		self.num_players = None
		self.max_util = None
		self.strategies = None
		self.seed = None
		
		# operation modes (pre-set to default behavior)
		self.fast_mode 		= True
		self.multithreading = True
		self.number_threads = min(os.cpu_count(), default_number_threads)  # Suggested to use at least 4 threads
		
		# gambit method (pre-set to default)
		self.gambit_method = application.NE_methods.pol  # default: gambit-enumpoly
		
		# domain method (pre-set to default)
		self.domain_method = application.domain_methods.decimal
		self.decimal_digits = default_number_decimal_digits
	
	def is_initialised(self):
		return self.init_method is not None
	
	def reset_input(self):
		# initialization method
		self.init_method = None
		self.init_from_file = None
		self.init_random = None
		self.seed = None
		
		# input file
		self.input_file = None
		
		# random parameters
		self.num_players = None
		self.max_util = None
		self.strategies = None
	
	def reset_default_settings(self):
		# operation modes (pre-set to default behavior)
		self.fast_mode = True
		self.multithreading = True
		self.number_threads = min(os.cpu_count(), default_number_threads)  # Suggested to use at least 4 threads
		
		# gambit method (pre-set to default)
		self.gambit_method = application.NE_methods.pol  # default: gambit-enumpoly
		
		# domain method (pre-set to default)
		self.domain_method = application.domain_methods.decimal
		self.decimal_digits = default_number_decimal_digits
	
	def create_command_vector(self):
		assert self.init_method is not None
		
		args = []
		
		## Initialization Method Arguments
		if self.init_method == init_method.file:
			args.append(application.args.file)
			args.append(self.input_file)
		
		else:  # self.init_method == init_method.reandom
			args.append(application.args.random)
			args.append(str(self.num_players))
			
			for player in range(self.num_players):
				args.append(str(self.strategies[player]))
			
			args.append(str(self.max_util))
			
			args.append(application.args.seed)
			args.append(str(self.seed))
		
		## Operation Arguments
		# fast mode
		if self.fast_mode: args.append(application.args.fast_mode)
		
		# multithreading
		if self.fast_mode and self.multithreading:
			args.append(application.args.mul_thred_tr)
			args.append(str(self.number_threads))
		
		# gambit method
		args.append(application.args.NE_method)
		args.append(self.gambit_method)
		
		# domain method
		args.append(application.args.domain)
		args.append(self.domain_method)
		if self.domain_method == application.domain_methods.decimal:
			args.append(str(self.decimal_digits))
		
		## Adding Quiet and No Output
		# Supress any output to terminal!
		# Comment these lines for debugging
		args.append(application.args.quiet)
		args.append(application.args.no_out)
		
		return args
	
	############
	# Mutators #
	############
	
	def set_init_file(self, filename):
		assert self.init_method is None
		
		self.init_method = init_method.file
		self.input_file = filename
	
	def set_init_random(self, num_players, strategies, max_utility, seed):
		assert self.init_method is None
		
		self.init_method = init_method.random
		self.num_players = num_players
		self.strategies = strategies
		self.max_util = max_utility
		self.seed = seed
	
	def set_settings(self, ne_method, decimal_digits, fast_mode, num_threads):
		self.gambit_method	= ne_method
		self.decimal_digits = decimal_digits
		self.fast_mode		= fast_mode
		
		if fast_mode:
			self.number_threads = num_threads