# -*- coding: utf-8 -*-
"""
Tutorial brain for the baseball experiment
"""

# pragma: no cover
__author__ = 'Adrian Hein'

from hbp_nrp_cle.brainsim import simulator as sim
import numpy as np
import nest


# one input neuron that fires if the ball is near enough
n_input = 2

# nine output neurons which are:
# 0: /robot/hollie_real_left_arm_0_joint/cmd_pos
# 1: /robot/hollie_real_left_arm_1_joint/cmd_pos
# 2: /robot/hollie_real_left_arm_2_joint/cmd_pos
# 3: /robot/hollie_real_left_arm_3_joint/cmd_pos
# 4: /robot/hollie_real_left_arm_4_joint/cmd_pos
# 5: /robot/hollie_real_left_arm_5_joint/cmd_pos
# 6: /robot/hollie_real_left_arm_6_joint/cmd_pos
# 7: /robot/hollie_real_left_hand_base_joint/cmd_pos
# 8: /robot/hollie_tennis_racket_joint/cmd_pos
# we have to try out which of them are important if we want to hit the ball in such way that it flies as far as possible
n_output = 7
input_neurons = sim.Population(n_input, cellclass=sim.IF_curr_exp())
output_neurons = sim.Population(n_output, cellclass=sim.IF_curr_exp())
#w = sim.RandomDistribution('gamma', [1, 0.004], rng=NumpyRNG(seed=4242))
connections = sim.Projection(input_neurons, output_neurons, sim.AllToAllConnector(allow_self_connections=False), sim.StaticSynapse(weight=1.))

circuit = input_neurons + output_neurons
