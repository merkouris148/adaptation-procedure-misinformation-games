###########################################################
# do_experiments.py
# --------------------------------------------------------
# Runs experiments for the Adaptation Procedure. Calls the
# Application class of application.py repeatedly.
# The output will be written in a csv file as a nx8 array.
# The delimiter is the space " ".
#
# Input: 	1. The number of the first experiment to be run.
#				A number in range {0, ..., 7}.
#
#			2. The number of the last experiment to be run.
#				A number in range {0, ..., 7}.
#
#			3. (Optionally) A file to write the output.
#
# Output:	The output has the following format. Each row
#			represents an instance of input. Each column
#			a data point. The data that are collected,
#			with respect to the order of columns are the
#			following:
#				
#				1. Number of Players
#				2. Number of Pure Strategy Profiles
#				3. Total time
#				4. CPU time
#				5. Number of nodes
#				6. Number of Unique Mis. Games
#				7. Number of Leaves
#				8. Number of unique mGs to Leaves
#				9. Number of SMEs
#
# Example call:
#	python do_experiments.py 2 2
#
#	Output to example:
#
#		| Doing experiment with strategy vectors: [3, 3]
#		|
#		|  Exp 1: [2, 9, 2.5839450359344482, 0.7580824660000001, 139, 44, 72, 41, 13]
#		|  Exp 2: [2, 9, 0.40831518173217773, 0.12158038500000012, 19, 8, 8, 7, 1]
#		|  Exp 3: [2, 9, 0.9016678333282471, 0.247497917, 62, 17, 43, 15, 2]
#		|  Exp 4: [2, 9, 0.045057058334350586, 0.01416062600000001, 3, 2, 1, 1, 1]
#		|  Exp 5: [2, 9, 2.897676944732666, 0.604542876, 84, 30, 45, 22, 9]
#		|
#		| Average: [ 2. 9. 0.45168002 0.12774631 28. 9. 17.33333333  7.66666667  1.33333333]
#		|
#		| Elapsed Time: 7.050811767578125(s)
#
#
# author: Merkouris Papamichail
# email: mercoyris@ics.forth.gr
# institute: ICS, FORTH
# last update: 13/4/2022
###########################################################


#############
# Libraries #
#############

## Python
import sys
import itertools
import time

## Custom
import application

## 3rd Party
import numpy as np		# 2D array & savetxt

#############
# Constants #
#############

rand_seed = [2, 3, 5, 7, 11]
max_util = 10

experiments =[[2, 2],			# 0. 2^4	= 16	SPs
			  [2, 3],			# 1. 2^6	= 64	SPs
			  [3, 3],			# 2. 2^9	= 512	SPs
			  [4, 3],			# 3. 2^12 	= 4096	SPs
			  [4, 4],			# 4. 2^16	= 65536 SPs
			  [2, 2, 2],		# 5. 2^8	= 256	SPs
			  [3, 2, 2],		# 6. 2^12	= 4096	SPs
			  [2, 2, 2, 2]]		# 7. 2^16	= 65536 SPs


#############
# Arguments #
#############

min_exp = int(sys.argv[1])
assert 0 <= min_exp and min_exp <= len(experiments) - 1
max_exp = int(sys.argv[2])
assert 0 <= max_exp and max_exp <= len(experiments) - 1
assert min_exp <= max_exp

out_to_file = True
if len(sys.argv) == 4:
	output	= sys.argv[3]
else:
	out_to_file = False

##################
# The Experiment #
##################


## starting experiment
start_t = time.time()

for i in range(min_exp, max_exp + 1):
	
	print("Doing experiment with strategy vectors: " + str(experiments[i]) + "\n")
	
	S = np.zeros(8)

	for j in range(1, 6):

		## construct the argument vector
		ad_argv = ["-fm", "-mtt", "4", "-no", "-se", str(rand_seed[j-1]), "-r", str(len(experiments[i]))]
		for s in experiments[i]:
			ad_argv += str(s)
		ad_argv += [str(max_util)]
		
		## run the experiment 
		app = application.Application(ad_argv)
		app.exec()
	
		# data
		data_vec = np.array(app.get_numerical_stats())
		
		print("  Exp " + str(j) + ": " + str(app.get_numerical_stats()))
		
		if j != 1 and j != 5:
			S += data_vec
	
	# calculate the average
	S = S / 3
	print("\nAverage: " + str(S))
	if out_to_file:
		f_out = open(output, "a")
		np.savetxt(f_out, S, fmt='%1.3f', newline=" ")
		f_out.write("\n")
		f_out.close()

## end experiment
end_t = time.time()
total_t = end_t - start_t


####################
# Print Some Stats #
####################

print("\n\nElapsed Time: " + str(total_t) + "(s)")
