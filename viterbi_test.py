#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
#                   GNU GENERAL PUBLIC LICENSE
#                       Version 2, June 1991
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# 
#   https://en.wikipedia.org/wiki/Viterbi_algorithm
#
import sys
import os
import re
import getopt
import glob

obs     = ('normal', 'cold', 'dizzy')
states  = ('Healthy', 'Fever')

start_p = {
            'Healthy': 0.6,
            'Fever': 0.4
        }
trans_p = {
            'Healthy' : {
                'Healthy': 0.7,
                'Fever'  : 0.3
            },
            'Fever' : {
                'Healthy': 0.4,
                'Fever'  : 0.6
            }
        }
emit_p  = {
            'Healthy' : {
                'normal' : 0.5,
                'cold'   : 0.4,
                'dizzy'  : 0.1
            },
            'Fever' : {
                'normal' : 0.1,
                'cold'   : 0.3,
                'dizzy'  : 0.6
            }
        }

def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    for st in states:
        V[0][st] = {"prob": start_p[st] * emit_p[st][obs[0]], "prev": None}
    # Run Viterbi when t > 0
    for t in range(1, len(obs)):
        V.append({})
        for st in states:
            max_tr_prob = max(V[t-1][prev_st]["prob"]*trans_p[prev_st][st] for prev_st in states)
            for prev_st in states:
                if V[t-1][prev_st]["prob"] * trans_p[prev_st][st] == max_tr_prob:
                    max_prob = max_tr_prob * emit_p[st][obs[t]]
                    V[t][st] = {"prob": max_prob, "prev": prev_st}
                    break
    for line in dptable(V):
        print(line)
    opt = []
    # The highest probability
    max_prob = max(value["prob"] for value in V[-1].values())
    previous = None
    # Get most probable state and its backtrack
    for st, data in V[-1].items():
        if data["prob"] == max_prob:
            opt.append(st)
            previous = st
            break
    # Follow the backtrack till the first observation
    for t in range(len(V) - 2, -1, -1):
        opt.insert(0, V[t + 1][previous]["prev"])
        previous = V[t + 1][previous]["prev"]

    print('The steps of states are ' + ' '.join(opt) + ' with highest probability of %s' % max_prob)

def dptable(V):
    # Print a table of steps from dictionary
    yield '  ' + " ".join(("%12d" % i) for i in range(len(V)))
    for state in V[0]:
        yield "%7.7s: " % state + " ".join("%12.8s" % ("%f" % v[state]["prob"]) for v in V)

if __name__ == '__main__':
    viterbi(obs, states, start_p, trans_p, emit_p)




