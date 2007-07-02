#!/usr/bin/python

import math
import pyNEAT

class XORTest:
   def __init__(self):
      self.inputs       = [[1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]]
      self.targets      = [0.0, 1.0, 1.0, 0.0]
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

      output = self.makeNeuron(pyNEAT.Neuron.OUTPUT, outputs, all)

      for i in range(2):
         hidden = self.makeNeuron(pyNEAT.Neuron.HIDDEN, hiddens, all)
         self.synapses.append(pyNEAT.Synapse(hidden, output, pyNEAT.random_utils.randfloat()))

      for i in range(3):
         input = self.makeNeuron(pyNEAT.Neuron.INPUT, inputs, all)
         for hidden in hiddens:
            self.synapses.append(pyNEAT.Synapse(input, hidden, pyNEAT.random_utils.randfloat()))

      return pyNEAT.NeuralNetwork(0, inputs, outputs, all)

   def run(self, fitnessThreshold):
      print "START XOR TEST"

      self.nn = self.makeNetwork()

      fitness = self.evaluate(False, False)

      count             = 0
      lastFitness       = 0
      lastFitnessChange = 0

      learningRate = 0.3
      momentum     = 0.1

      while fitness < fitnessThreshold:
         count += 1

         show = False
         #if (count % 100) == 0:
         #   show = True

         fitness = self.evaluate(show, True, learningRate)

         if (count % 100) == 0:
            print 'fitness =', fitness

         #if (count % 1000) == 0:
         #   learningRate *= momentum

         if lastFitness != 0 and lastFitness == int(fitness):
            lastFitnessChange += 1
         else:
            lastFitness       = int(fitness)
            lastFitnessChange = 0

         if lastFitnessChange > 1000:
            print 'network appears to have stagnated... perturbing network'
            for synapse in self.synapses:
               synapse.perturb()
            lastFitnessChange = 0

      self.evaluate(True, False)
      self.nn.dump('nn.out')

      print "END XOR TEST"

   def evaluate(self, show=False, backprop=True, learningRate=0.3):
      networkDepth = self.nn.getMaxDepth()

      outputs = []

      for i in range(len(self.inputs)):
         self.nn.setInput(self.inputs[i])

         self.nn.activate()
         for j in range(networkDepth):
            self.nn.activate()

         output = self.nn.outputs[0].output
         outputs.append(output)

         if show:
            self.printOutput(self.inputs[i], self.targets[i], output)

         if backprop:
            self.nn.backPropagate([self.targets[i]], learningRate)

         self.nn.clear()

      sse  = pyNEAT.Fitness.sumSquaredError(outputs, self.targets)
      rmse = pyNEAT.Fitness.rootMeanSquaredError(outputs, self.targets)
      me   = pyNEAT.Fitness.meanError(outputs, self.targets)

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

def trainTest():
   xorTest = XORTest()
   xorTest.run(99)

def loadTest():
   xorTest = XORTest()
   xorTest.nn = pyNEAT.NeuralNetwork(0)
   xorTest.nn.load('nn.out')
   xorTest.evaluate(True, False)


if __name__ == '__main__':
   trainTest()
   #loadTest()
