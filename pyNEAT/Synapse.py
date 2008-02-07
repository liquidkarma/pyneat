"""
pyNEAT
Copyright (C) 2007-2008 Brian Greer

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

import random

class Synapse:
   def __init__(self, input, output, weight, recurrent = False, trait = None):
      self.input     = input
      self.output    = output
      self.weight    = weight
      self.recurrent = recurrent
      self.trait     = trait
      self.enabled   = True

      if output is not None:
         self.output.synapses.append(self)

   def deriveTrait(self, trait):
      self.params = trait.params

   def perturb(self, sigma=0.75):
      self.weight += random.gauss(0.0, sigma)
