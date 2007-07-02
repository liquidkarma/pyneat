import time

from Configuration import *
from Genome        import *
from Population    import *
from ExperimentUI  import *

class Experiment:
   def __init__(self, name, start_genes_filename=None, ui=ExperimentUI):
      self.name               = name
      self.startGenesFileName = start_genes_filename
      self.ui                 = ui(self)
      self.uiRunning          = False

   def runUI(self):
      self.uiRunning = True
      self.ui.run()
      self.uiRunning = False

   def run(self, startGenesFileName=None, generations=Configuration.numGenerations):
      if not self.uiRunning:
         self.oldUI = self.ui
         self.ui    = ExperimentConsoleUI(self)

      self.ui.startTest(self.name)

      if startGenesFileName is None:
         startGenome = Genome(fileName=self.startGenesFileName)
      else:
         startGenome = Genome(fileName=startGenesFileName)

      for i in range(Configuration.numRuns):
         self.ui.setRun(i)
         self.population = Population(startGenome)
         for generation in range(generations):
            self.ui.setGeneration(generation)
            startTime = time.clock()
            self.epoch(generation)
            endTime = time.clock()
            self.ui.setGenerationTime(endTime - startTime)

      self.ui.endTest(self.name)

      if not self.uiRunning:
         self.ui = self.oldUI

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

      self.ui.setHighestFitness(self.population.highestFitness)
      self.evaluate(self.population.champion.network, True)

      if winner:
         self.ui.winnerFound()

   def displayNetwork(self, network, showWeights=False):
      self.ui.displayNetwork(network, showWeights)

   def displayOutputs(self, outputs):
      self.ui.displayOutputs(self.targets, outputs)

   def evaluate(self):
      raise NotImplementedError, 'Please override the \'evaluate\' method in your experiment class'
