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

import random
import math
import time

from Configuration import *
from Mutator       import *
from Species       import *
from Organism      import *
from Genome        import *

class Population:
   def __init__(self, genome=None, size=-1, numInputs=0, numOutputs=0, maxHidden=0, linkProbability=0.0, recurrent=False):
      if size < 0:
         size = Configuration.populationSize

      self.winnerGeneration     = 0
      self.highestFitness       = 0.0
      self.highestLastChanged   = 0

      self.currentNeuronId      = 0
      self.currentInnovationId  = 0

      self.champion = None

      self.species     = []
      self.organisms   = []
      self.innovations = []

      if genome is None:
         numNodes                 = numInputs + numOutputs + maxHidden
         self.currentNeuronId     = numNodes + 1
         self.currentInnovationId = numNodes * numNodes + 1

         for i in range(size):
            self.organisms.append(Genome(i, numInputs, numOutputs, random.randint(0, maxHidden), maxHidden, recurrent, linkProbability))

         self.speciate()
      else:
         self.spawn(genome, size)

   def spawn(self, genome, size):
      for i in range(size):
         newGenome = genome.makeCopy(i)

         newGenome.mutateSynapseWeights(1.0, 1.0, Mutator.GAUSSIAN)

         self.organisms.append(Organism(0.0, newGenome, 1))

         self.currentNeuronId     = newGenome.getLastNeuronId()
         self.currentInnovationId = newGenome.getLastGeneInnovationId()

      self.speciate()

   def speciate(self):
      self.species = None
      counter      = 0

      for organism in self.organisms:
         addSpecies = True

         if self.species is None:
            self.species = []
         else:
            for specie in self.species:
               for compareOrganism in specie.organisms:
                  if organism.isCompatibleWith(compareOrganism):
                     specie.addOrganism(organism)
                     addSpecies = False
                     break

               if not addSpecies:
                  break

         if addSpecies:
            counter += 1
            newSpecies = Species(counter)
            newSpecies.addOrganism(organism)
            self.species.append(newSpecies)

   def epoch(self, generation, experiment, debug=True):
      for organism in self.organisms:
         fitness, outputs, error, won = experiment.evaluate(organism.network)

         organism.fitness = fitness
         organism.outputs = outputs
         organism.error   = error
         organism.winner  = won

      numSpecies   = len(self.species)
      numOrganisms = len(self.organisms)

      if Configuration.enforceDiversification:
         if generation > 1:
            if numSpecies < Configuration.numSpeciesTarget:
               Configuration.compatibilityThreshold -= 0.3
            elif numSpecies > Configuration.numSpeciesTarget:
               Configuration.compatibilityThreshold += 0.3

            if Configuration.compatibilityThreshold < 0.3:
               Configuration.compatibilityThreshold = 0.3

      for specie in self.species:
         specie.calcFitnessStats()
         specie.adjustFitness()

      totalFitness = 0
      for organism in self.organisms:
         totalFitness += organism.fitness

      overallAverage = totalFitness / numOrganisms

      if debug:
         print "Generation:", generation, ", Total fitness:", totalFitness, ", Overall average:", overallAverage

      for organism in self.organisms:
         organism.expectedOffspring = organism.fitness / overallAverage

      skim = 0.0
      totalExpected = 0
      for specie in self.species:
         skim           = specie.countOffspring(skim)
         totalExpected += specie.expectedOffspring

      if totalExpected < numOrganisms:
         maxExpected   = 0
         finalExpected = 0

         bestSpecie = None

         for specie in self.species:
            if specie.expectedOffspring > maxExpected:
               maxExpected = specie.expectedOffspring
               bestSpecie  = specie

            finalExpected += specie.expectedOffspring

         if bestSpecie is not None:
            bestSpecie.expectedOffspring += 1
            finalExpected += 1

         if finalExpected < numOrganisms:
            if debug:
               print "Population died!"
            for specie in self.species:
               specie.expectedOffspring = 0
            if bestSpecie is not None:
               bestSpecie.expectedOffspring = numOrganisms

      #startTime = time.clock()

      sortedSpecies = list(self.species)
      sortedSpecies.sort()

      #endTime = time.clock()
      #print 'sort time:', (endTime - startTime)

      bestSpeciesId = sortedSpecies[0].id

      if debug:
         for specie in sortedSpecies:
            print "Original fitness of species", specie.id, "( Size", len(specie.organisms), "):", specie.organisms[0].originalFitness, "last improved", (specie.age - specie.ageOfLastImprovement)

      # check for population stagnation
      self.champion = sortedSpecies[0].organisms[0]
      self.champion.populationChampion = True

      if self.champion.originalFitness > self.highestFitness:
         self.highestFitness = self.champion.originalFitness
         self.highestLastChanged = 0
      else:
         self.highestLastChanged += 1
         if debug:
            print self.highestLastChanged, "generations since last population fitness record:", self.highestFitness

      # delta coding
      if self.highestLastChanged >= (Configuration.dropoffAge + 5):
         if debug:
            print "PERFORMING DELTA CODING"

         self.highestLastChanged = 0

         halfPopulationSize = Configuration.populationSize / 2

         self.champion.superChampionOffspring  = halfPopulationSize
         sortedSpecies[0].expectedOffspring    = halfPopulationSize
         sortedSpecies[0].ageOfLastImprovement = sortedSpecies[0].age

         if len(sortedSpecies) > 1:
            sortedSpecies[1].organisms[0].superChampionOffspring = Configuration.populationSize - halfPopulationSize
            sortedSpecies[1].expectedOffspring                   = Configuration.populationSize - halfPopulationSize
            sortedSpecies[1].ageOfLastImprovement                = sortedSpecies[1].age

            # remove all other species
            for i in range(2, len(sortedSpecies)):
               sortedSpecies[i].expectedOffspring = 0
         else:
            self.champion.superChampionOffspring += Configuration.populationSize - halfPopulationSize
            sortedSpecies[0].expectedOffspring    = Configuration.populationSize - halfPopulationSize
      elif Configuration.babiesStolen > 0:
         stolenBabies = 0

         for specie in reversed(sortedSpecies):
            if specie.age > 5 and specie.expectedOffspring > 2:
               if (specie.expectedOffspring - 1) >= (Configuration.babiesStolen - stolenBabies):
                  specie.expectedOffspring -= Configuration.babiesStolen - stolenBabies
                  break
               else:
                  stolenBabies += specie.expectedOffspring - 1
                  specie.expectedOffspring = 1

                  if stolenBabies >= Configurtion.babiesStolen:
                     break

         oneFifthStolen = Configuration.babiesStolen / 5
         oneTenthStolen = Configuration.babiesStolen / 10

         championCount = 0

         for specie in sortedSpecies:
            if championCount < 2:
               if specie.lastImproved() <= Configuration.dropoffAge and stolenBabies >= oneFifthStolen:
                  specie.organisms[0].superChampionOffspring = oneFifthStolen
                  specie.expectedOffspring += oneFifthStolen
                  stolenBabies -= oneFifthStolen
                  championCount += 1
            elif championCount == 2:
               if specie.lastImproved() <= Configuration.dropoffAge and stolenBabies >= oneTenthStolen:
                  specie.organisms[0].superChampionOffspring = oneTenthStolen
                  specie.expectedOffspring += oneTenthStolen
                  stolenBabies -= oneTenthStolen
                  championCount += 1
            elif stolenBabies > 0:
               if randfloat() > 0.1:
                  if stolenBabies > 3:
                     specie.organisms[0].superChampionOffspring = 3
                     specie.expectedOffspring += 3
                     stolenBabies -= 3
                  else:
                     specie.organisms[0].superChampionOffspring = stolenBabies
                     specie.expectedOffspring += stolenBabies
                     stolenBabies = 0
                     break
            else:
               break

         if stolenBabies > 0:
            self.champion.superChampionOffspring += stolenBabies
            sortedSpecies[0].expectedOffspring   += stolenBabies
            stolenBabies                          = 0

      # delete eliminated organisms
      for organism in self.organisms:
         if organism.eliminated:
            organism.species.removeOrganism(organism)
            self.organisms.remove(organism)

      if debug:
         print "Reproducing"
         startTime = time.clock()

      for specie in self.species:
         specie.reproduce(generation, self, sortedSpecies)

      if debug:
         endTime = time.clock()
         print "Reproduction complete (time", (endTime - startTime), ")"

      for organism in self.organisms:
         organism.species.removeOrganism(organism)
      self.organisms = []

      # filter out species with no organisms
      self.species = [specie for specie in self.species if len(specie.organisms) > 0]

      organismCount = 0
      for specie in self.species:
         if specie.novel:
            specie.novel = False
         else:
            specie.age += 1

         for organism in specie.organisms:
            organism.setId(organismCount)
            organismCount += 1
            self.organisms.append(organism)

      self.innovations = []

      # make sure the best species did not die accidentally
      found = False
      for specie in self.species:
         if specie.id == bestSpeciesId:
            found = True
            break;

      if debug and not found:
         print "ERROR: Best species died!"

   def getNextInnovationId(self, inc=1):
      id = self.currentInnovationId
      self.currentInnovationId += inc
      return id

   def getNextNeuronId(self):
      id = self.currentNeuronId
      self.currentNeuronId += 1
      return id
