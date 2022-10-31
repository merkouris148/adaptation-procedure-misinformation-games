# A class tha provides various methods of
# finding the Nash Equilibria of a NFG.
# Currently, only supports two command-line
# commands of GAMBIT. Namely:
#
#   1. General Newton Method (gambit-gnm)
#       for n-player games
#
#   2. Extreme Point Enumeration (gambit-enummixed)
#       for 2-player games
#
# The default method
#

#############
# Constants #
#############

# Python3 does not provide an "infinite"
# Integer, we assign a huge value
max_players = 2**32

#############
# Libraries #
#############

import subprocess

###########
# Classes #
###########

class method_vals:
    gnm_val = 0
    xpe_val = 1
    enp_val = 2     # enumerate pure
    pol_val = 3


method_vals = method_vals()


method_vals_list = [
    method_vals.gnm_val,
    method_vals.xpe_val,
    method_vals.enp_val,
    method_vals.pol_val
]


class method_names:
    gnm = "Generalized Newton Method"
    xpe = "Extreme Point Enumeration"
    enp = "Enumerate Pure Nash Equilibria"
    pol = "Support Enumeration"

method_names = method_names()

method_names_list = [
    method_names.gnm,
    method_names.xpe,
    method_names.enp,
    method_names.pol
]

# the maximum number of players
# that the method can support

class method_max_players:
    gnm = max_players
    xpe = 2
    enp = max_players
    pol = max_players

method_max_players = method_max_players()

method_max_players_list = [
    method_max_players.gnm,
    method_max_players.xpe,
    method_max_players.enp,
    method_max_players.pol
]

class Gambit:

    def __init__(self, decimal = 8, method_val = method_vals.pol_val, timeout = 1):
        assert method_val in method_vals_list
        assert decimal > 0

        # Set the number opf decimal points
        self.decimal = decimal

        # Set a timeout for the sub-process calls
        self.timeout = timeout

        # The method whose behaviour will mirror in the method
        # compute_nash_equilibria()
        self.default_method_val = method_val

    #############
    # Accessors #
    #############

    def get_default_method_val(self):
        return self.default_method_val

    def get_default_method_name(self):
        return method_names_list[self.default_method_val]

    ###########
    # Methods #
    ###########

    def generalized_newton_method(self, nfg_file, n_perturb=100):
        try:
            gambit_call = subprocess.run(
                [
                    "gambit-gnm",
                    "-q",
                    "-d " + str(self.decimal),
                    "-n",
                    str(n_perturb)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                input=nfg_file,
                timeout=self.timeout
            )

            gambit_out = gambit_call.stdout
            if gambit_out == None:
                print("Warning: Gambit: No Nash Equilibria found before timeout")
                return None
            else:
                #return "\n".join(list(set(gambit_out.split('\n'))))
                return list(set(gambit_out.split('\n')))

        except subprocess.TimeoutExpired as time_out:
            gambit_out = time_out.stdout
            if gambit_out == None:
                print("Warning: Gambit: No Nash Equilibria found before timeout")
                return None
            else:
                #return "\n".join(list(set(gambit_out.decode("utf-8").split('\n'))))
                return list(set(gambit_out.decode("utf-8").split('\n')))

    def extreme_point_enumeration(self, nfg_file):
        try:
            gambit_call = subprocess.run(
                [
                    "gambit-enummixed",
                    "-q",
                    "-d " + str(self.decimal)
                ],
                stdout=subprocess.PIPE,
                stderr = subprocess.DEVNULL,
                text=True,
                input=nfg_file,
                timeout=self.timeout
            )

            gambit_out = gambit_call.stdout
            if gambit_out == None:
                print("Warning: Gambit: No Nash Equilibria found before timeout")
                return None
            else:
                # return "\n".join(list(set(gambit_out.split('\n'))))
                return list(set(gambit_out.split('\n')))

        except subprocess.TimeoutExpired as time_out:
            gambit_out = time_out.stdout
            if gambit_out == None:
                print("Warning: Gambit: No Nash Equilibria found before timeout")
                return None
            else:
                # return "\n".join(list(set(gambit_out.decode("utf-8").split('\n'))))
                return list(set(gambit_out.decode("utf-8").split('\n')))

    def enumerate_pure_equlibria(self, nfg_file):
        try:
            gambit_call = subprocess.run(
                [
                    "gambit-enumpure",
                    "-q"#,
                    #"-d 8"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                input=nfg_file,
                timeout=self.timeout
            )

            gambit_out = gambit_call.stdout
            if gambit_out == None:
                print("Warning: Gambit: No Nash Equilibria found before timeout")
                return None
            else:
                # return "\n".join(list(set(gambit_out.split('\n'))))
                return list(set(gambit_out.split('\n')))

        except subprocess.TimeoutExpired as time_out:
            gambit_out = time_out.stdout
            if gambit_out == None:
                print("Warning: Gambit: No Nash Equilibria found before timeout")
                return None
            else:
                # return "\n".join(list(set(gambit_out.decode("utf-8").split('\n'))))
                return list(set(gambit_out.decode("utf-8").split('\n')))

    def support_enumeration(self, nfg_file):
        try:
            gambit_call = subprocess.run(
                [
                    "gambit-enumpoly",
                    "-q",
                    "-H",
                    "-d " + str(self.decimal)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                input=nfg_file,
                timeout=self.timeout
            )

            gambit_out = gambit_call.stdout
            if gambit_out == None:
                print("Warning: Gambit: No Nash Equilibria found before timeout")
                return None
            else:
                # return "\n".join(list(set(gambit_out.split('\n'))))
                return list(set(gambit_out.split('\n')))

        except subprocess.TimeoutExpired as time_out:
            gambit_out = time_out.stdout
            if gambit_out == None:
                print("Warning: Gambit: No Nash Equilibria found before timeout")
                return None
            else:
                # return "\n".join(list(set(gambit_out.decode("utf-8").split('\n'))))
                return list(set(gambit_out.decode("utf-8").split('\n')))

    def compute_nash_equilibria(self, nfg_file):

        if self.default_method_val == method_vals.gnm_val:
            return self.generalized_newton_method(nfg_file)

        if self.default_method_val == method_vals.xpe_val:
            return self.extreme_point_enumeration(nfg_file)

        if self.default_method_val == method_vals.enp_val:
            return self.enumerate_pure_equlibria(nfg_file)

        if self.default_method_val == method_vals.pol_val:
            return self.support_enumeration(nfg_file)