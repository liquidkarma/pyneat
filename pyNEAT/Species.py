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
import random

from Configuration import *
from Mutator       import *
from Organism      import *
from Genome        import *
from Crossover     import *
from random_utils  import *

class Species:
   def __init__(self, id, novel=False):
      self.id                   = id
      self.age                  = 1
      self.aveFitness           = 0.0
      self.maxFitness           = 0
      self.overallMaxFitness    = 0
      self.expectedOffspring    = 0
      self.novel                = novel
      self.ageOfLastImprovement = 0
      self.organisms            = []

   # descending order of fitness
   def __cmp__(self, other):
      if len(self.organisms) > 0:
         if len(other.organisms) > 0:
            return self.organisms[0].__cmp__(other.organisms[0])
         else:
            return 1
      elif len(other.organisms) > 0:
         return -1
      else:
         return 0

   def addOrganism(self, organism):
      self.organisms.append(organism)
      organism.species = self

   def removeOrganism(self, organism):
      if organism in self.organisms:
         self.organisms.remove(organism)

   def adjustFitness(self):
      ageDebt = self.age - self.ageOfLastImprovement + 1 - Configuration.dropoffAge
      if ageDebt == 0:
         ageDebt = 1

      numOrganisms = len(self.organisms)

      for organism in self.organisms:
         organism.originalFitness = organism.fitness

         if ageDebt >= 1:
            # possible graded dropoff
            #organism.fitness = organism.fitness * math.atan(ageDebt)
            organism.fitness = organism.fitness * 0.01
         if self.age <= 10:
            organism.fitness *= Configuration.ageSignificance

         if organism.fitness < 0.0:
            organism.fitness = 0.0001

         organism.fitness = organism.fitness / numOrganisms

      self.organisms.sort()

      if self.organisms[0].originalFitness > self.overallMaxFitness:
         self.ageOfLastImprovement = self.age
         self.overallMaxFitness    = self.organisms[0].originalFitness

      self.organisms[0].speciesChampion = True

      numParents = int(math.floor(Configuration.survivalThreshold * numOrganisms + 1.0))

      if numParents < numOrganisms:
         for i in range(numParents + 1, numOrganisms):
            self.organisms[i].eliminated = True

   def calcFitnessStats(self):
      self.maxFitness = 0.0
      total = 0.0
      for organism in self.organisms:
         total += organism.fitness
         if organism.fitness > self.maxFitness:
            self.maxFitness = organism.fitness
      self.aveFitness = total / len(self.organisms)

   def lastImproved(self):
      return self.age - self.ageOfLastImprovement

   def reproduce(self, generation, population, species):
      poolSize = len(self.organisms) - 1

      if poolSize >= 0:
         champion = self.organisms[0]

         championDone = False

         mutationPower = Configuration.weightMutationPower

         for i in range(int(self.expectedOffspring)):
            baby = None

            mutateBabyStructure = False
            mateBaby            = False

            if champion.superChampionOffspring > 0:
               mom       = champion
               newGenome = mom.genome.makeCopy(i)

               if champion.superChampionOffspring > 1:
                  if randfloat() < 0.8 or Configuration.mutateAddSynapseProbability == 0.0:
                     newGenome.mutateSynapseWeights(Mutator.GAUSSIAN, mutationPower, 1.0)
                  else:
                     netAnalogue = newGenome.genesis(generation)
                     newGenome.mutateAddSynapse(population, Configuration.synapseAddTries)
                     mutateBabyStructure = True

               baby = Organism(0.0, newGenome, generation)

               if champion.superChampionOffspring == 1:
                  if champion.populationChampion:
                     baby.populationChampionChild = True
                     baby.maxFitness              = mom.originalFitness

               champion.superChampionOffspring -= 1

            elif not championDone and self.expectedOffspring > 5:
               mom       = champion
               newGenome = mom.genome.makeCopy(i)

               baby         = Organism(0.0, newGenome, generation)
               championDone = True

            elif poolSize == 0 or randfloat() < Configuration.mutateOnlyProbability:
               mom          = self.organisms[random.randint(0, poolSize)]
               newGenome    = mom.genome.makeCopy(i)

               if randfloat() < Configuration.mutateAddNeuronProbability:
                  newGenome.mutateAddNeuron(population)
                  mutateBabyStructure = True
               elif randfloat() < Configuration.mutateAddSynapseProbability:
                  netAnalogue = newGenome.genesis(generation)
                  newGenome.mutateAddSynapse(population, Configuration.synapseAddTries)
                  mutateBabyStructure = True
               else:
                  newGenome.tryAllMutations(mutationPower)

               baby = Organism(0.0, newGenome, generation)

            else:
               mom = self.organisms[random.randint(0, poolSize)]
               dad = None

               if randfloat() > Configuration.interspeciesMateRate:
                  dad = self.organisms[random.randint(0, poolSize)]
               else:
                  otherSpecies = None

                  for tries in range(5):
                     randMultiplier = random.gauss(0, 1) / 4.0
                     if randMultiplier > 1.0:
                        randMultiplier = 1.0

                     speciesIndex = int(math.floor((randMultiplier * (len(species) - 1.0)) + 0.5))
                     otherSpecies = species[speciesIndex]
                     if self != otherSpecies:
                        break
                     else:
                        otherSpecies = None

                  if otherSpecies is not None:
                     dad = otherSpecies.organisms[0]
                  else:
                     dad = mom

               if randfloat() < Configuration.mateMultipointProbability:
                  newGenome = mom.genome.crossover(Crossover.MULTIPOINT, dad.genome, i, mom.originalFitness, dad.originalFitness)
               elif randfloat() < (Configuration.mateMultipointAveProbability / (Configuration.mateMultipointAveProbability + Configuration.mateSinglepointProbability)):
                  newGenome = mom.genome.crossover(Crossover.MULTIPOINT_AVG, dad.genome, i, mom.originalFitness, dad.originalFitness)
               else:
                  newGenome = mom.genome.crossover(Crossover.SINGLEPOINT, dad.genome, i)

               mateBaby = True

               if randfloat() > Configuration.mateOnlyProbability or dad.genome.id == mom.genome.id or dad.genome.getCompatibility(mom.genome) == 0.0:
                  if randfloat() < Configuration.mutateAddNeuronProbability:
                     newGenome.mutateAddNeuron(population)
                     mutateBabyStructure = True
                  elif randfloat() < Configuration.mutateAddSynapseProbability:
                     netAnalogue = newGenome.genesis(generation)
                     newGenome.mutateAddSynapse(population, Configuration.synapseAddTries)
                     mutateBabyStructure = True
                  else:
                     newGenome.tryAllMutations(mutationPower)

               baby = Organism(0.0, newGenome, generation)

            baby.mutateBabyStructure = mutateBabyStructure
            baby.mateBaby            = mateBaby

            found = False

            for specie in population.species:
               for organism in specie.organisms:
                  if baby.isCompatibleWith(organism):
                     specie.addOrganism(baby)
                     baby.species = specie
                     found = True
                     break
               if found:
                  break

            if not found:
               newSpecies = Species(len(population.species) + 1, novel=True)
               newSpecies.addOrganism(baby)
               baby.species = newSpecies
               population.species.append(newSpecies)

   def countOffspring(self, skim):
      self.expectedOffspring = 0

      for organism in self.organisms:
         eoWhole      = math.floor(organism.expectedOffspring)
         eoFractional = math.fmod(organism.expectedOffspring, 1.0)

         self.expectedOffspring += eoWhole
         skim                   += eoFractional

         if skim > 1.0:
            skimWhole = math.floor(skim)
            self.expectedOffspring += skimWhole
            skim -= skimWhole

      return skim

