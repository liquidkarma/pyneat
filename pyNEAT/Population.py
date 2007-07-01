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

      self.winnerGeneration   = 0
      self.highestFitness     = 0.0
      self.highestLastChanged = 0

      self.currentNeuronId    = 0
      self.currentInnovation  = 0

      self.champion = None

      self.species     = []
      self.organisms   = []
      self.innovations = []

      if genome is None:
         self.currentNeuronId     = numInputs + numOutputs + maxHidden
         self.currentInnovationId = self.currentNeuronId * self.currentNeuronId + 1

         self.currentNeuronId += 1

         for i in range(size):
            self.organisms.append(Genome(i, numInputs, numOutputs, random.randint(0, maxHidden), maxHidden, recurrent, linkProbability))

         self.speciate()
      else:
         self.spawn(genome, size)

   def spawn(self, genome, size):
      for i in range(size):
         newGenome           = Genome(genome.id, genome.neurons, genome.genes, genome.traits)
         newGenome.phenotype = genome.phenotype
         newGenome.id        = i

         newGenome.mutateSynapseWeights(1.0, 1.0, Mutator.GAUSSIAN)

         self.organisms.append(Organism(0.0, newGenome, 1))

         self.currentNeuronId     = newGenome.getLastNeuronId()
         self.currentInnovationId = newGenome.getLastGeneInnovationId()

      self.speciate()

   def speciate(self):
      self.species = None
      counter      = 0

      for organism in self.organisms:
         if self.species is None:
            counter += 1
            newSpecies = Species(counter)
            newSpecies.addOrganism(organism)
            organism.species = newSpecies
            self.species = [newSpecies]
         else:
            foundSpecies = False

            for specie in self.species:
               for compareOrganism in specie.organisms:
                  if organism.isCompatibleWith(compareOrganism):
                     specie.addOrganism(organism)
                     organism.species = specie
                     foundSpecies = True
                     break

               if foundSpecies:
                  break

            if not foundSpecies:
               counter += 1
               newSpecies = Species(counter)
               newSpecies.addOrganism(organism)
               organism.species = newSpecies
               self.species.append(newSpecies)

   def epoch(self, generation):
      numSpecies   = len(self.species)
      numOrganisms = len(self.organisms)

      # enforce diversification
      #if generation > 1:
      #   if numSpecies < Configuration.numSpeciesTarget:
      #      Configuration.compatibilityThreshold -= 0.3
      #   elif numSpecies > Configuration.numSpeciesTarget:
      #      Configuration.compatibilityThreshold += 0.3
      #
      #   if Configuration.compatibilityThreshold < 0.3:
      #      Configuration.compatibilityThreshold = 0.3

      for specie in self.species:
         specie.adjustFitness()

      totalFitness = 0
      for organism in self.organisms:
         totalFitness += organism.fitness

      overallAverage = totalFitness / numOrganisms

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
            print "Population died!"
            for specie in self.species:
               specie.expectedOffspring = 0
            if bestSpecie is not None:
               bestSpecie.expectedOffspring = numOrganisms

      startTime = time.clock()

      sortedSpecies = list(self.species)
      sortedSpecies.sort()

      endTime = time.clock()
      print 'sort time:', (endTime - startTime)

      bestSpeciesId = sortedSpecies[0].id

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
         print self.highestLastChanged, "generations since last population fitness record:", self.highestFitness

      # delta coding
      if self.highestLastChanged >= (Configuration.dropoffAge + 5):
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

         sortedSpecies.reverse()

         for specie in sortedSpecies:
            if specie.age > 5 and specie.expectedOffspring > 2:
               if (specie.expectedOffspring - 1) >= (Configuration.babiesStolen - stolenBabies):
                  specie.expectedOffspring -= Configuration.babiesStolen - stolenBabies
                  break
               else:
                  stolenBabies += specie.expectedOffspring - 1
                  specie.expectedOffspring = 1

                  if stolenBabies >= Configurtion.babiesStolen:
                     break

         # restore original order
         sortedSpecies.reverse()

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

      print "Reproducing"
      startTime = time.clock()

      for specie in self.species:
         specie.reproduce(generation, self, sortedSpecies)

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
            organism.genome.id = organismCount
            organismCount += 1
            self.organisms.append(organism)

      self.innovations = []

      # make sure the best species did not die accidentally
      found = False
      for specie in self.species:
         if specie.id == bestSpeciesId:
            found = True
            break;

      if not found:
         print "ERROR: Best species died!"

