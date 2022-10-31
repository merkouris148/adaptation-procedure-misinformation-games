def parse_gambit_out_file(num_players, strategies_vec, gambit_out_file):
	assert  num_players >= 2
	assert len(strategies_vec) == num_players

	## filtering out empty lines
	gambit_out_file = list(filter(lambda line: line != "", gambit_out_file))
	## Assert, that gambit_out_file:
	#	i) is a non empty list,
	#	ii) of non empty lines
	#assert gambit_out_file, "Error: No Nash Equilibrium found in Input File!"


	## A list of strategy profiles
	nash_equilibria = []


	for line in gambit_out_file:
		nash_equilibrium = parse_gambit_out_line(num_players, strategies_vec, line)
		nash_equilibria.append(nash_equilibrium)


	return nash_equilibria


def parse_gambit_out_line(num_players, strategies_vec, line):
	assert line != ""

	tokens = line.split(",")
	tokens.pop(0)					# Discard the first token, as is the "NE" keyword

	cursor = 0
	strategy_prof = []
	for player in range(num_players):
		strategy = []
		for i in range(strategies_vec[player]):
			strategy.append(float(tokens[cursor]))
			cursor += 1

		tup_strategy = tuple(strategy)
		strategy_prof.append(tup_strategy)

	tup_strategy_prof = tuple(strategy_prof)

	return tup_strategy_prof