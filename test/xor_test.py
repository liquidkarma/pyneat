#!/usr/bin/python

import math
import profile
import pyNEAT

class XORTest(pyNEAT.Experiment):
   def __init__(self):
      pyNEAT.Experiment.__init__(self, 'XOR', 'xorstartgenes')
      self.inputs  = [[1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]]
      self.targets = [0.0, 1.0, 1.0, 0.0]

   def evaluate(self, network, printNetwork=False):
      networkDepth = network.getMaxDepth()

      outputs = []

      for input in self.inputs:
         network.setInput(input)
         network.activate()
         for i in range(networkDepth):
            network.activate()
         outputs.append(network.outputs[0].output)
         network.clear()

      errorSum = 0
      winner   = True

      for i in range(len(self.targets)):
         errorSum += math.fabs(outputs[i] - self.targets[i])
         if (self.targets[i] > 0.5 and outputs[i] < 0.5) or \
            (self.targets[i] < 0.5 and outputs[i] > 0.5):
            winner = False

      fitness = (4.0 - errorSum) ** 2
      error   = errorSum

      if printNetwork:
         self.displayNetwork(network, True)
         self.displayOutputs(outputs)

      return fitness, error, winner

if __name__ == '__main__':
   xorTest = XORTest()
   xorTest.run()
   #xorTest.runUI()
   #profile.run("xorTest.run()")
