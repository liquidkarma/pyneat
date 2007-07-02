import time

from Configuration import *
from Genome        import *
from Population    import *
from ExperimentGUI import *

class Experiment:
   def __init__(self, name):
      self.gui  = ExperimentGUI()
      self.name = name

   def run(self, startGenesFileName, generations=Configuration.numGenerations):
      self.gui.startTest(self.name)

      startGenome = Genome(fileName=startGenesFileName)

      for i in range(Configuration.numRuns):
         self.gui.setRun(i)
         self.population = Population(startGenome)
         for generation in range(generations):
            self.gui.setGeneration(generation)
            startTime = time.clock()
            self.epoch(generation)
            endTime = time.clock()
            self.gui.setGenerationTime(endTime - startTime)

      self.gui.endTest(self.name)

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

      self.gui.setHighestFitness(self.population.highestFitness)
      self.evaluate(self.population.champion.network, True)

      if winner:
         self.gui.winnerFound()

   def displayNetwork(self, network, showWeights=False):
      self.gui.displayNetwork(network, showWeights)

   def displayOutputs(self, outputs):
      self.gui.displayOutputs(self.targets, outputs)

   def evaluate(self):
      raise NotImplementedError, 'Please override the \'evaluate\' method in your experiment class'
