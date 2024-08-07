#####################################################################
# main.py
# ------------------------------------------------------------------
#
# This file contains the "main" function for the implementation of
# the adaptation procedure in misinformation games. Observe that only
# contains calls to the Application class of the application.py file.
#
# author: Merkouris Papamichail
# email: mercoyris@ics.forth.gr
# institute: ICS, FORTH
# last update: 13/4/2022
#####################################################################
# yo!

#############
# Libraries #
#############

# python libraries
import time
import threading

# custom libraries
import application

# python libraries
import random
import sys


## Create App
app = application.Application(sys.argv)

## Exec App
app.exec()
