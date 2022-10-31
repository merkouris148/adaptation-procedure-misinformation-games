#############
# Libraries #
#############

import auxiliary_functions as ax
import os

class Debugging:

	def __init__(self, print_warnings = False, die_after_warning = False):

		## Counters
		self.gambit_calls 		= 0
		self.clingo_calls 		= 0
		#self.num_voronoi_cells	= 0

		## Timers
		self.total_gambit_time = 0
		self.total_clingo_time = 0

		## Warning Counters
		self.zeros_mixed_strategy 	= 0		# GAMBIT returned a strategy of the form (0, 0, .., 0)
		self.mixed_strat_lt_one		= 0		# the probabilities of a mixed strategy don't add to 1
		self.no_nash				= 0		# a GAMBIT call returned no nash equilibria

		## Multithreading
		self.hardware_threads = os.cpu_count()
		self.too_many_threads = False

		## States
		self.print_warnings 	= print_warnings
		self.die_after_warning	= die_after_warning


	#############
	# Accessors #
	#############

	# GAMBIT
	def get_total_gambit_time(self):
		return self.total_gambit_time

	def get_gambit_calls(self):
		return self.gambit_calls

	def get_average_gambit_time(self):
		return self.total_gambit_time / self.gambit_calls


	## CLINGO
	def get_total_clingo_time(self):
		return self.total_clingo_time

	def get_clingo_calls(self):
		return self.clingo_calls

	def get_average_clingo_time(self):
		return self.total_clingo_time / self.clingo_calls


	## Warnings
	def get_zeros_mixed_strategy(self):
		return self.zeros_mixed_strategy

	def get_mixed_strat_lt_one(self):
		return self.mixed_strat_lt_one

	def get_no_nash(self):
		return self.no_nash

	def get_too_many_threads(self):
		return self.too_many_threads

	## One get to rule them all
	def get_stats(self):

		return [self.get_total_gambit_time(),
				self.get_gambit_calls(),
				self.get_average_gambit_time(),
				self.get_total_clingo_time(),
				self.get_clingo_calls(),
				self.get_average_clingo_time(),
				self.get_zeros_mixed_strategy(),
				self.get_mixed_strat_lt_one(),
				self.get_no_nash(),
				self.get_too_many_threads()]

	###################
	# Subsystem Calls #
	###################

	## 	GAMBIT
	def gambit_call(self, time):
		assert time >= 0

		self.gambit_calls += 1
		self.total_gambit_time += time

	## CLINGO
	def clingo_call(self, time):
		assert time >= 0

		self.clingo_calls += 1
		self.total_clingo_time += time


	######################
	# Tests for Warnings #
	######################

	def check_zeros_mixed_strategy(self, strategy_profile_list):

		for strategy_profile in strategy_profile_list:
			if ax.sp_is_zeros(strategy_profile):
				self.zeros_mixed_strategy += 1		# increase the warning counter

				if self.print_warnings:
					print("Debugging Warning: strategy profile " + str(strategy_profile) + " has a zeros mixed strategy!")

				if self.die_after_warning:
					print("Debugging: Exiting after warning zeros_mixed_strategy.")
					os._exit(1)

	def check_mixed_strat_lt_one(self, strategy_profile_list):

		for strategy_profile in strategy_profile_list:
			if ax.sp_lt_one(strategy_profile):
				self.mixed_strat_lt_one += 1

				if self.print_warnings:
					print("Debugging Warning: strategy profile " + str(strategy_profile) + " has a mixed strategy of sum less than one!")

				if self.die_after_warning:
					print("Debugging: Exiting after warning mixed_strat_lt_one.")
					os._exit(1)

	def check_no_nash(self, nash_equilibria_list):

		if nash_equilibria_list == []:
			self.no_nash += 1

			if self.print_warnings:
				print("Debugging Warning: No Nash Equilibria found!")

			if self.die_after_warning:
				print("Debugging: Exiting after warning no_nash.")
				os._exit(1)

	def check_num_threads(self, mtt_num_threads):

		if mtt_num_threads > self.hardware_threads:
			self.too_many_threads = True

			if self.print_warnings:
				print("Debugging Warning: Too many threads, defined " + str(mtt_num_threads) + " this computer only has " + str(self.hardware_threads) + "!")

			if self.die_after_warning:
				print("Exiting after too many threads defined " + str(mtt_num_threads) + "/" + str(self.hardware_threads) + "!")
				os._exit(1)


