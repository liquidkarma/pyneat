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

from Configuration import *
from random_utils  import *

class Trait:
   def __init__(self, id=-1, t1=None, t2=None, config=None):
      self.id     = id
      self.params = []

      if t1 is not None and t2 is not None:
         self.id = t1.id
         for i in range(Configuration.numTraitParams):
            self.params.append((t1.params[i] + t2.params[i]) / 2.0)
      elif config is not None:
         self.id = int(config.pop(0))
         for param in config:
            self.params.append(float(param))
         deltaParams = Configuration.numTraitParams - len(config)
         if deltaParams > 0:
            for i in range(deltaParams):
               self.params.append(0)
         elif deltaParams < 0:
            self.params = self.params[:Configuration.numTraitPrams]
      else:
         for i in range(Configuration.numTraitParams):
            self.params.append(0)

   def mutate(self):
      for param in self.params:
         if randfloat() > Configuration.traitParamMutationProbability:
            param += randposneg() * randfloat() * Configuration.traitMutationPower
            if param < 0:
               param = 0
