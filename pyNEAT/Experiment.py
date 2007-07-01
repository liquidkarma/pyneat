import time

from Configuration import *
from Genome        import *
from Population    import *

class Experiment:
   def __init__(self):
      pass

   def run(self, startGenesFileName, generations=Configuration.numGenerations):
      startGenome = Genome(fileName=startGenesFileName)

      for i in range(Configuration.numRuns):
         print "Run:", i
         self.population = Population(startGenome)
         for generation in range(generations):
            print "Generation:", generation
            startTime = time.clock()
            self.epoch(generation)
            endTime = time.clock()
            print "Time:", (endTime - startTime)

   def epoch(self, generation):
      winner = False

      for organism in self.population.organisms:
         fitness, error, won = self.evaluate(organism.network)

         organism.fitness = fitness
         organism.error   = error
         organism.winner  = won

         if won:
            winner = True

      for specie in self.population.species:
         specie.getAverageFitness()
         specie.getMaxFitness()

      self.population.epoch(generation)

      print 'Highest fitness:', self.population.highestFitness
      self.evaluate(self.population.champion.network, True)

      if winner:
         print "Found winner"

   def evaluate(self):
      raise NotImplementedError, 'Please override the \'evaluate\' method in your experiment class'
