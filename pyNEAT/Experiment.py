import time

from Configuration import *
from Genome        import *
from Population    import *
from ExperimentUI  import *

class Run:
   def __init__(self, id, generation):
      self.id         = id
      self.generation = generation

class Experiment:
   def __init__(self, name, start_genes_filename=None, generations=Configuration.numGenerations, ui=ExperimentUI):
      self.name               = name
      self.startGenesFileName = start_genes_filename
      self.generations        = generations
      self.ui                 = ui(self)

   def run(self, useGUI=False):
      if not useGUI:
         self.oldUI = self.ui
         self.ui    = ExperimentConsoleUI(self)

      self.ui.run()

      if not useGUI:
         self.ui = self.oldUI

   def getRuns(self):
      startGenome = Genome(fileName=self.startGenesFileName)

      for i in range(Configuration.numRuns):
         self.population = Population(startGenome)
         for generation in range(self.generations):
            run = Run(i, generation)

            startTime = time.clock()
            self.epoch(generation, run)
            endTime = time.clock()

            run.time = endTime - startTime
            yield run

   def epoch(self, generation, run):
      run.winner = None

      for organism in self.population.organisms:
         fitness, outputs, error, won = self.evaluate(organism.network)

         organism.fitness = fitness
         organism.error   = error
         organism.winner  = won

         if won:
            run.winner = organism.network.id

      for specie in self.population.species:
         specie.getAverageFitness()
         specie.getMaxFitness()

      self.population.epoch(generation)

      fitness, outputs, error, won = self.evaluate(self.population.champion.network)

      run.champion = self.population.champion.network
      run.fitness  = self.population.highestFitness
      run.targets  = self.targets
      run.outputs  = outputs

   def displayNetwork(self, network, showWeights=False):
      self.ui.displayNetwork(network, showWeights)

   def displayOutputs(self, outputs):
      self.ui.displayOutputs(self.targets, outputs)

   def evaluate(self, network, printNetwork=False):
      raise NotImplementedError, 'Please override the \'evaluate\' method in your experiment class'
