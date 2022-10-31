%%%%%%%%%%
% Player %
%%%%%%%%%%

player(Player) :-
	num_players(NumPlayers),
	Player = 1..NumPlayers.



%%%%%%%%
% Game %
%%%%%%%%

game(Game) :- Game == 0.	% The actual game
game(Game) :- player(Game).	% Some player's game




%%%%%%%%%%%%%%%%%%%%%
% Number Strategies %
%%%%%%%%%%%%%%%%%%%%%

%% compute the number of strategies
number_strategies(Player, NumStrat) :-
	player(Player),
	NumStrat = #count{1,S : s(Player, S)}.




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The Strategy of a Player in a SP %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% the strategy of a player in a strategy profile
player_strategy(Player, SP, S) :-
	player_strategy(Player, SP, 1, S).

%Base case: current player = player
player_strategy(Player, sp(S, SP), Player, S) :-
	player(Player),
	s(Player, S),
	strategy_profile(SP, Player+1).

%current player < player
player_strategy(Player, sp(X, SP), CurrentPlayer, S) :-
	player(Player),
	player(CurrentPlayer),
	CurrentPlayer < Player,
	s(CurrentPlayer, X),
	player_strategy(Player, SP, CurrentPlayer+1, S).




%%%%%%%%%%%%%%%%%%%%
% Strategy Profile %
%%%%%%%%%%%%%%%%%%%%

strategy_profile(SP) :- strategy_profile(SP, 1).

strategy_profile(nul, NP+1) :- num_players(NP).
strategy_profile(sp(X, SP), Player) :-
	s(Player, X),
	strategy_profile(SP, Player+1).




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Number of Strategy Profiles %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% compute the number of strategy profiles
number_strategy_profiles(NumSPs) :-
	num_players(NumPlayers),
	number_strategy_profiles(NumPlayers, NumSPs).

number_strategy_profiles(0, 1).
number_strategy_profiles(Player + 1, PartProduct) :-
	player(Player+1),
	number_strategies(Player+1, NumStratPl),
	PartProduct == NumStratPl * PartProduct1,
	number_strategy_profiles(Player, PartProduct1).
