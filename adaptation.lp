%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% addaptation.pl
% --------------------------------------------------------
% Input:	~Misinformation Game~
%		~as list of N+1 Normal Form Games~
%		* num_players/1, e.g. num_players(N).
%			The number of players.
%
%		* s/2, s(<player>, <strategy>).
%			The strategies of player <player>.
%		
%		* u/4, describing the utilities of the game
%			e.g. u(<game>, <player>, <strategy_profile>, <utility>).
%			the field <game> is an integer describing whose player
%			this game is. <game> \in {0, 1, ..., N}, where N is the
%			number of players and
%			<game> = 0 is the *actual* game the N players are playing.
%
%			~Natural Misinformed Equilibria~
%		* nme/1, e.g. nme(<strategy_profile>)
%			a (pure) strategy profile, that is a Natural Misinformed
%			Equilibrium.
%			NOTE: There should be *ONLY ONE* such predicate! in order
%			to the resulting MG to be well defined, i.e. unique.
%
% Output:	~Misinformation Game~
%		* v/4, describing the utilities of the resulting game.
%
%			NOTE: 1) We only compute the resulting utilities predicate,
%			denoted with v/4, since the other predicates remain the same.
%			
%			2) Let u(g, p, sp) be an input utility function, also, let
%			NME be a nme strategy profile. For the resulting utility
%			function we have,
%							_
%						   |	u(0, p, sp),	if sp = NME
%			v(g, p, sp) = <
%						   |	u(g, p, sp),	otherwise
%							-
%
% author: Merkouris Papamichail
% email: mercoyris@ics.forth.gr
% institute: ICS, FORTH
% last update: 13/4/2022
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#include "misinformation_game.lp".

%% DEBUG
%pos(sp(1, sp(1, sp(1, nul)))).

%% addaptation step
%% NOTE: a *single* pos/1 predicate should be provided
v(G, P, SP, V) :-
	game(G), player(P),
	strategy_profile(SP), pos(SP),
	u(0, P, SP, U),	V = U.

v(G, P, SP, V) :-
	game(G), player(P),
	strategy_profile(SP), not pos(SP),
	u(G, P, SP, U),	V = U.
	
% check if the utilities have changed after one
% addaptation step. If the utilities have changed,
% this results to a new MG.
changed :- v(G, P, SP, V), u(G, P, SP, U), game(G), strategy_profile(SP), player(P), V != U.
unchanged :- not changed.


% we "put" this token to the answer set for technical
% reasons, namely, for the python to can easily "grap"
% the line containing the answer set form the clingo
% output.
answer_set.


% Knowledge
new_knowledge(Player, N) :-
    player(Player),
    N = #count{SP, P : v(0, P, SP, V), v(Player, P, SP, V), player(P)}.

new_knowledge(N) :-
    N = #sum{NP, Player : new_knowledge(Player, NP), player(Player)}.

old_knowledge(Player, N) :-
    player(Player),
    N = #count{SP, P : u(0, P, SP, U), u(Player, P, SP, U), player(P)}.

old_knowledge(N) :-
    N = #sum{NP, Player : old_knowledge(Player, NP), player(Player)}.

total_knowledge(N) :-
    number_strategy_profiles(NumSPs),
    num_players(NumPlayers),
    N = NumSPs * NumPlayers * NumPlayers.

new_frac_knowledge(K, T) :-
    new_knowledge(K),
    total_knowledge(T).

old_frac_knowledge(K, T) :-
    old_knowledge(K),
    total_knowledge(T).

% Test Changed
% outputs the triples (G, P, SP) that have changed
% in the resulting MG.
% changed(G, P, SP) :- v(G, P, SP, V), u(G, P, SP, U), V != U.

% directives
#show v/4.
#show changed/0.
#show unchanged/0.
#show answer_set/0.
%#show new_knowledge/1.
%#show new_knowledge/2.
%#show old_knowledge/1.
%#show old_knowledge/2.
#show new_frac_knowledge/2.
#show old_frac_knowledge/2.

% Testing
%#show changed/3.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%		Example
% ------------------------------------
% 1. changed(1,1,sp(1,sp(1,sp(1,nul))))
% 2. changed(1,2,sp(1,sp(1,sp(1,nul))))
% 3. changed(1,3,sp(1,sp(1,sp(1,nul))))
% 4. changed(2,1,sp(1,sp(1,sp(1,nul))))
% 5. changed(2,2,sp(1,sp(1,sp(1,nul)))) 
% 6. changed(2,3,sp(1,sp(1,sp(1,nul))))
% 7. changed(3,1,sp(1,sp(1,sp(1,nul))))
% 8. changed(3,2,sp(1,sp(1,sp(1,nul))))
% 9. changed(3,3,sp(1,sp(1,sp(1,nul))))
%
% We have # games x # players = 3 x 3 = 9
% changed utility entries.
% Observe that the will be either 0 changed
% entries, or # games x # players.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
