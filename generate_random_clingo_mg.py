##########################################################################
# A tool for generating random clingo MG files
#
# Input:
#	1. Number of players
#	2. The number of strategies of each player separated by space ' '
#	3. Maximum Utility
#
# Output:
#	A .lp file printed.
##########################################################################

#############
# Libraries #
#############

## Python Libraries
import sys

## Custom Libraries
import gambit
import debugging
import domain
import misinformation_game


## Handle arguments
assert sys.argv[1].isdigit()
num_players = int(sys.argv[1])

# Handle strategies
assert len(sys.argv) == num_players + 3
strategies = []
for player in range(2, 2 + num_players):
	assert sys.argv[player].isdigit()
	strategies.append(int(sys.argv[player]))

# handle max utility
assert sys.argv[2 + num_players].isdigit()
max_util = int(sys.argv[2 + num_players])


## Handle the "context"
# create a gambit instance
Gambit = gambit.Gambit()

# create a debugging instance
Debug = debugging.Debugging()

# create a domain instance
Domain = domain.SPDomain()

## Give a game id
game_id = 0

## Create an MG
MG = misinformation_game.MisinformationGame(
	Gambit,
	Debug,
	Domain,
	game_id,
	num_players,
	strategies
)

# random utilities
MG.generate_random_utilities(max_util)

# generate clingo file
MG.clingo_compile_format()

# print clingo file
print(MG.get_clingo_format())