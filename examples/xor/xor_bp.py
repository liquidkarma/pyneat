#!/usr/bin/python

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

## This is examples learns XOR using the backprop algorithm included in pyNEAT

import sys
import os.path
import pyNEAT

from pyNEAT.BackPropTester import BackPropTester

pyNEAT.Configuration.printEvery = 100

class XORTest(BackPropTester):
   def __init__(self):
      BackPropTester.__init__(self, 'BP-XOR')

      self.inputs       = [[1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]]
      self.targets      = [[0.0], [1.0], [1.0], [0.0]]

      self.numInputs    = len(self.inputs[0])
      self.numHidden    = 2
      self.numOutputs   = 1

def trainTest():
   xorTest = XORTest()
   xorTest.run(99.5)

def loadTest(loadFile):
   xorTest = XORTest()
   xorTest.nn = pyNEAT.NeuralNetwork(0)
   xorTest.nn.load(loadFile)
   xorTest.evaluate(True, False)


if __name__ == '__main__':
   loadFile = 'nn.out'
   if len(sys.argv) > 1 and sys.argv[1] == 'load' and os.path.exists(loadFile):
      loadTest(loadFile)
   else:
      trainTest()
