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

import pyNEAT
import time

class BackPropTester:
   def __init__(self, name):
      self.name = name
      self.ui   = pyNEAT.ExperimentUI(self)

      self.inputs  = []
      self.targets = []
      self.outputs = []

      self.nextNeuronId = 1

   def makeNeuron(self, type, pool, all):
      neuron = pyNEAT.Neuron(self.nextNeuronId, type)
      self.nextNeuronId += 1

      if pool is not None:
         pool.append(neuron)

      all.append(neuron)

      return neuron

   def makeNetwork(self):
      self.synapses = []

      inputs  = []
      hiddens = []
      outputs = []
      all     = []

      for i in range(self.numOutputs):
         self.makeNeuron(pyNEAT.Neuron.OUTPUT, outputs, all)

      for i in range(self.numHidden):
         hidden = self.makeNeuron(pyNEAT.Neuron.HIDDEN, hiddens, all)
         for output in outputs:
            self.synapses.append(pyNEAT.Synapse(hidden, output, pyNEAT.random_utils.randfloat()))

      for i in range(self.numInputs):
         input = self.makeNeuron(pyNEAT.Neuron.INPUT, inputs, all)
         for hidden in hiddens:
            self.synapses.append(pyNEAT.Synapse(input, hidden, pyNEAT.random_utils.randfloat()))

      return pyNEAT.NeuralNetwork(0, inputs, outputs, all)

   def run(self, fitnessThreshold):
      self.fitnessThreshold = fitnessThreshold
      self.ui.run()

   def getRuns(self):
      self.nn = self.makeNetwork()

      fitness = self.evaluate(False, False)

      count             = 0
      lastFitness       = 0.0
      lastFitnessChange = 0

      learningRate      = 0.3
      momentum          = 0.1

      generations       = pyNEAT.Configuration.numGenerations
      runs              = pyNEAT.Configuration.numRuns

      runCount          = 0

      startTime         = time.clock()
      endTime           = 0

      while fitness < self.fitnessThreshold:
         count += 1

         show = False
         #if (count % 100) == 0:
         #   show = True

         fitness = self.evaluate(show, True, learningRate)

         if (count % 100) == 0:
            runCount += 1
            run = pyNEAT.Run(runCount, 0)

            endTime  = time.clock()
            run.time = endTime - startTime

            run.winner   = None
            run.champion = self.nn
            run.fitness  = fitness
            run.targets  = self.targets
            run.outputs  = self.outputs

            yield run

            startTime = time.clock()

         #if (count % 1000) == 0:
         #   learningRate *= momentum

         #if lastFitness != 0 and lastFitness == int(fitness):
         #   lastFitnessChange += 1
         #else:
         #   lastFitness       = int(fitness)
         #   lastFitnessChange = 0

         #if fitness > lastFitness:
         if float('%.3f' % fitness) > float('%.3f' % lastFitness):
            lastFitness       = fitness
            lastFitnessChange = 0
         else:
            lastFitnessChange += 1

         if lastFitnessChange > 1000:
            print 'network appears to have stagnated... perturbing network'
            self.nn.display()
            for synapse in self.synapses:
               synapse.perturb()
            self.nn.display()
            lastFitnessChange = 0

      self.evaluate(True, False)
      self.nn.dump('nn.out')

   def evaluate(self, show=False, backprop=True, learningRate=0.3):
      networkDepth = self.nn.getMaxDepth()

      self.outputs = []

      for i in range(len(self.inputs)):
         self.nn.setInput(self.inputs[i])

         self.nn.activate()
         for j in range(networkDepth):
            self.nn.activate()

         output = [x.output for x in self.nn.outputs]
         self.outputs.append(output)

         if show:
            self.printOutput(self.inputs[i], self.targets[i], output)

         if backprop:
            self.nn.backPropagate(self.targets[i], learningRate)

         self.nn.clear()

      sse  = pyNEAT.Fitness.sumSquaredError(self.outputs, self.targets)
      rmse = pyNEAT.Fitness.rootMeanSquaredError(self.outputs, self.targets)
      me   = pyNEAT.Fitness.meanError(self.outputs, self.targets)

      fitness = (10.0 - rmse) ** 2

      if show:
         print 'sse =', sse
         print 'rmse =', rmse
         print 'me =', me
         print 'fitness =', fitness

      return fitness

   def printOutput(self, inputs, target, output):
      print '[',
      for input in inputs:
         print input,
      print '] [', target, '] =', output
