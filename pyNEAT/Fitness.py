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

def getError(outputs, targets):
   if len(targets) != len(outputs):
      raise Exception('Invalid number of targets')

   error = 0.0

   for i in range(len(targets)):
      output = outputs[i]
      target = targets[i]
      if len(output) != len(target):
         raise Exception('Invalid target size')
      for j in range(len(target)):
         delta = output[j] - target[j]
         error += delta * delta

   return error

#def getError(outputs, targets):
#   deltas = [map(lambda i, j: (i - j) * (i - j), x, y) for x, y in zip(outputs, targets)]
#   return reduce(lambda x, y: x + y, deltas)

def sumSquaredError(outputs, targets):
   error = getError(outputs, targets)
   return math.sqrt(error)

def rootMeanSquaredError(outputs, targets):
   error = getError(outputs, targets)
   return math.sqrt(error / len(targets))

def meanError(outputs, targets):
   return getError(outputs, targets) * 0.5
