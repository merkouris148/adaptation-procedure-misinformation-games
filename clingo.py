###########################################################
# clingo.py
# --------------------------------------------------------
# A system call to clingo shell command.
#
# Input:
#	1. String clingo_mg_file, a string containing the
#		description of a MG in clingo predicates.
#
#	2. String clingo_nme, a string containing *a single*
#		predicate describing a nme.
#
#	3. File clingo_axioms, a file containing the axioms
#		(clingo rules) to compute an addaptation step,
#		given a MG and a nme.
#
#		By Default: clingo_axioms = "./addaptation.pl"
#
# Output:
#	* String answer_set, a string conatining the predicates
#		computed by clingo.
#	
#	NOTE:	1) The answer set, for technical reasons, is
#			containing the predicate answer_set/0.
#
#			2) Also, if the NFG has changed through the
#			addaptation step, the predicate changed/0.
#			will be in the answer set. If not, the the
#			predicate unchanged/0. will hold.
#
# See also: addaptation.pl for further documentation.
#
# author: Merkouris Papamichail
# email: mercoyris@ics.forth.gr
# institute: ICS, FORTH
# last update: 13/4/2022
###########################################################

import subprocess


def addaptation_step(clingo_mg_file, clingo_nme, clingo_axioms="./adaptation.lp"):
	f = open(clingo_axioms, "r")
	input = f.read() + clingo_mg_file + "\n" + clingo_nme + "\n"
	f.close()
	
	clingo_call = subprocess.run(
		[
			"clingo",
			"-t",
			"4"
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.DEVNULL,
		text=True,
		input=input
	)
	
	for line in clingo_call.stdout.split("\n"):
		if "answer_set" in line:
			answer_set = line
	
	return answer_set
