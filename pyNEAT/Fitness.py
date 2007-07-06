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

def sumSquaredError(outputs, targets):
   if len(targets) != len(outputs):
      raise Exception('Invalid number of targets')

   error = 0.0

   for i in range(len(targets)):
      delta = outputs[i] - targets[i]
      error += delta * delta

   return math.sqrt(error)

def rootMeanSquaredError(outputs, targets):
   if len(targets) != len(outputs):
      raise Exception('Invalid number of targets')

   error = 0.0

   for i in range(len(targets)):
      delta = outputs[i] - targets[i]
      error += delta * delta

   return math.sqrt(error / len(targets))

def meanError(outputs, targets):
   if len(targets) != len(outputs):
      raise Exception('Invalid number of targets')

   error = 0.0

   for i in range(len(targets)):
      delta = outputs[i] - targets[i]
      error += delta * delta

   return error * 0.5
