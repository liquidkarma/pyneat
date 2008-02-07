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

## Simple XOR experiment. This should be the minimum amount of effort required
## to create an experiment with pyNEAT.

import pyNEAT
import math
#import profile

class XORTest(pyNEAT.Experiment):
   def __init__(self):
      pyNEAT.Experiment.__init__(self, 'XOR', 'xorstartgenes')
      self.inputs  = [[1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]]
      self.targets = [0.0, 1.0, 1.0, 0.0]

   def evaluate(self, network):
      outputs  = network.activate(inputs=self.inputs)
      errorSum = 0
      winner   = True

      for i in range(len(self.targets)):
         target = self.targets[i]
         output = outputs[i][0]

         errorSum += math.fabs(output - target)
         if (target > 0.5 and output < 0.5) or \
            (target < 0.5 and output > 0.5):
            winner = False

      fitness = (4.0 - errorSum) ** 2
      error   = errorSum

      return fitness, outputs, error, winner

if __name__ == '__main__':
   pyNEAT.loadConfiguration('xor.ne')
   xorTest = XORTest()
   xorTest.run(useGUI=True)
   #profile.run("xorTest.run()")
