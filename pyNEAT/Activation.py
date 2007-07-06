"""
pyNEAT
Copyright (C) 2007 Brian Greer

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import math

# RIGHT SHIFTED
# ave 3213 clean on 40 runs of p2m and 3468 on another 40
# 41394 with 1 failure on 8 runs
#def sigmoid_right(x):
#   return (1.0 / (1.0 + math.exp(-(slope * x - constant))))

# LEFT SHIFTED
# original setting ave 3423 on 40 runs of p2m, 3729 and 1 failure also
#def sigmoid_left(x):
#   return (1.0 / (1.0 + math.exp(-(slope * x + constant))))

# LEFT SHIFTED NON-STEEPENED
# simple left shifted
#def sigmoid_leftnonsteepened():
#   return (1.0 / (1.0 + math.exp(-x - constant)))

# NON-SHIFTED STEEPENED
def sigmoid_nonshifted(x, slope):
   return (1.0 / (1.0 + math.exp(-(slope * x))))

def dsigmoid_nonshifted(x, slope):
   return (slope * x * (1.0 - x))

# TANH SIGMOID
def sigmoid_tanh(x):
   return math.tanh(x)

def dsigmoid_tanh(x):
   return (1.0 - x * x)

# SIN SIGMOID
def sigmoid_sin(x):
   return math.sin(x)

# COS SIGMOID
def sigmoid_cos(x):
   return math.cos(x)

def sigmoid_gauss(x):
   return math.exp(-1 * (x ** 2))

# PLAIN SIGMOID
def sigmoid(x):
   return (1.0 / (1.0 + math.exp(-x)))

def dsigmoid(x):
   return (x * (1.0 - x))

# actual activation functions used
def activate(x, slope, constant):
   return sigmoid_nonshifted(x, slope)

def dactivate(x, slope, constant):
   return dsigmoid_nonshifted(x, slope)
