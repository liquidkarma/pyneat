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

class Organism:
   def __init__(self, fitness, genome, generation):
      self.originalFitness         = fitness
      self.fitness                 = fitness
      self.genome                  = genome
      self.generation              = generation
      self.species                 = None
      self.expectedOffspring       = 0
      self.maxFitness              = 0.0
      self.eliminated              = False

      self.superChampionOffspring  = 0
      self.populationChampion      = False
      self.populationChampionChild = False

      self.speciesChampion         = False

      self.network                 = genome.genesis(genome.id)

   # descending order of fitness
   def __cmp__(self, other):
      return other.originalFitness - self.originalFitness

   def isCompatibleWith(self, organism):
      return self.genome.isCompatibleWith(organism.genome)

   def setId(self, id):
      self.genome.id  = id
      self.network.id = id
