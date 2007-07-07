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
   def __init__(self, name, start_genes_filename=None, generations=None, runs=None, ui=ExperimentUI):
      self.name               = name
      self.startGenesFileName = start_genes_filename
      self.generations        = generations
      self.runs               = runs
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

      generations = self.generations
      runs        = self.runs

      if generations is None:
         generations = Configuration.numGenerations

      if runs is None:
         runs = Configuration.numRuns

      for i in range(runs):
         self.population = Population(startGenome)
         for generation in range(generations):
            run = Run(i, generation)

            startTime = time.clock()
            self.epoch(generation, run)
            endTime = time.clock()

            run.time = endTime - startTime
            yield run

   def epoch(self, generation, run):
      self.population.epoch(generation, self)

      if self.population.champion.winner:
         run.winner = self.population.champion.network.id
      else:
         run.winner = None

      run.champion = self.population.champion.network
      run.fitness  = self.population.highestFitness
      run.targets  = self.targets
      run.outputs  = self.population.champion.outputs

   def evaluate(self, network):
      raise NotImplementedError, 'Please override the \'evaluate\' method in your experiment class'
