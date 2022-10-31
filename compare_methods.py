##################################################################
# compare_methods.py
# ---------------------------------------------------------------
# E.g.: python compare_methods.py <s1> <s2> <max_util> <n_exp>
#
# Arguments:
#		<s1> The number of strategies of pl. 1
#		<s2> The number of strategies of pl. 2
#		<max_util> The maximum utilities
#		<n_exp> the number of experiments
#
# Function:
#		Generates <n_exp> number of 2-player
#		misinformation games using as seed the first
#		<n_exp> prime numbers.
#
################################################################


#############
# Libraries #
#############

# Python
import sys

# Custom
import auxiliary_functions as ax
import application as app


#############
# Arguments #
#############

## check number of arguments
assert len(sys.argv) == 5
s1 			= int(sys.argv[1])
s2 			= int(sys.argv[2])
max_util	= int(sys.argv[3])
n_exp		= int(sys.argv[4])

assert s1 >= 2
assert s2 >= 2
assert max_util >= 1
assert n_exp >= 0


##################
# Run Experiment #
##################

## Generate primes
seeds = ax.n_primes(n_exp)

n_smes_gnm = []
gnm_time = []
n_smes_xpe = []
xpe_time = []

gnm_zeros_mixed = []
xpe_zeros_mixed = []

#print(seeds)
for i in range(0, n_exp):
	print("\n\nExperiment " + str(i))
	## Generalized Newton Method
	# construct the arguments vector
	print("\tsupport enumeration\n")
	gnm_argv = ["-nem", "pol", "-fm", "-no", "-se", str(seeds[i]), "-r", "2", str(s1), str(s2), str(max_util), "-dbg"]
	gnm_app = app.Application(gnm_argv)
	gnm_app.exec()

	n_smes_gnm.append(gnm_app.get_stats()[10])
	gnm_time.append(gnm_app.get_stats()[3])
	gnm_zeros_mixed.append(gnm_app.get_stats()[17])
	#print("\nGNM #SMEs: " + str(gnm_app.get_stats()[-1]))

	## Extreme Point Enumeration
	# construct the arguments vector
	print("\n\textreme point enumeration\n")
	xpe_argv = ["-nem", "gnm", "-fm", "-no", "-se", str(seeds[i]), "-r", "2", str(s1), str(s2), str(max_util), "-dbg"]
	xpe_app = app.Application(xpe_argv)
	xpe_app.exec()

	n_smes_xpe.append(xpe_app.get_stats()[10])
	xpe_time.append(xpe_app.get_stats()[3])
	xpe_zeros_mixed.append(xpe_app.get_stats()[17])
	#print("\nXPE #SMEs: " + str(xpe_app.get_stats()[-1]))

	print("Zeros Mixed: POL" + str(gnm_app.get_stats()[17]) + "/ GNM" + str(xpe_app.get_stats()[17]), end="\r")

#diff_n_smes = []
#print(n_smes_xpe)
#print(n_smes_gnm)
#print("\n\t## Difference in SMEs ##")
#for i in range(0, n_exp):
#	diff_n_smes.append(n_smes_xpe[i] - n_smes_gnm[i])
#	print("Exp " + str(i) + ": " + "SMEs POL: " + str(n_smes_gnm[i]) + " SMEs XPE: " + str(n_smes_xpe[i]))

#print("\n\t## Difference in time ##")
#for i in range(0, n_exp):
#	print("Exp " + str(i) + ": GNM time: " + str(gnm_time[i]) + " XPE time: " + str(xpe_time[i]))

#S = 0
#xpe_more_smes = []
#gnm_more_smes = []
#for i in range(0, n_exp):
#	S += abs(diff_n_smes[i])
#	if diff_n_smes[i] > 0:
#		xpe_more_smes.append(1)
#	else:
#		xpe_more_smes.append(0)
#
#	if diff_n_smes[i] < 0:
#		gnm_more_smes.append(1)
#	else:
#		gnm_more_smes.append(0)
#
#sum_xpe_more_smes = sum(xpe_more_smes)
#sum_gnm_more_smes = sum(gnm_more_smes)
#
#avg_xpe_more_smes = sum_xpe_more_smes / n_exp
#avg_gnm_more_smes = sum_gnm_more_smes / n_exp
#
#Avg = S / n_exp

#print("\nAverage Difference in SMEs: " + str(Avg))
#print("Average More SMEs in XPE: " + str(avg_xpe_more_smes))
#print("Average More SMEs in POL: " + str(avg_gnm_more_smes))
