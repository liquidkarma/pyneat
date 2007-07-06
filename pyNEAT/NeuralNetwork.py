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

from Configuration import *
from Neuron        import *
from Synapse       import *

import Activation

class NeuralNetwork:
   def __init__(self, id=-1, inputs=None, outputs=None, all=None):
      self.id         = id
      self.inputs     = inputs
      self.outputs    = outputs
      self.allNeurons = all
      self.genotype   = None
      self.depth      = -1

   def activate(self, debug=False):
      for neuron in self.allNeurons:
         if neuron.active:
            neuron.activate(debug)

   def isRecurrent(self, input, output, count, threshold):
      if count > threshold:
         return False
      elif input.id == output.id:
         return True
      else:
         for synapse in input.synapses:
            if not synapse.recurrent:
               if self.isRecurrent(synapse.input, output, count + 1, threshold):
                  return True

      return False

   def display(self, showWeights=True):
      print 'Network', self.id
      for neuron in self.allNeurons:
         for synapse in neuron.synapses:
            if showWeights:
               print '\t', synapse.input.id, '-(', synapse.weight, ')->', neuron.id
            else:
               print '\t', synapse.input.id, '->', neuron.id

   def getMaxDepth(self):
      if self.depth < 0:
         self.depth = 0
         for output in self.outputs:
            depth = output.getMaxDepth()
            if depth > self.depth:
               self.depth = depth
         return self.depth
      else:
         return self.depth

   def setInput(self, values):
      valueIndex = 0
      for input in self.inputs:
         if input.type == Neuron.INPUT or input.type == Neuron.BIAS:
            input.input = values[valueIndex]
            valueIndex += 1

   def clear(self):
      for output in self.outputs:
         output.clear()

   def backPropagate(self, targets, learningRate=0.3):
      if len(targets) != len(self.outputs):
         raise Exception('Invalid number of targets')

      outputDelta = {}
      for i in range(len(targets)):
         outputDelta[self.outputs[i].id] = (targets[i] - self.outputs[i].output) * Activation.dactivate(self.outputs[i].output, Configuration.sigmoidSlope, Configuration.sigmoidConstant)

      self.__propagate(self.outputs, outputDelta, learningRate, [])

   def __propagate(self, neurons, deltas, learningRate, seenNeurons):
      errors      = {}
      nextDeltas  = {}
      nextNeurons = {}

      for i in range(len(neurons)):
         neuron = neurons[i]
         delta  = deltas[neuron.id]
         seenNeurons.append(neuron)
         for synapse in neuron.synapses:
            if synapse.input is not None and synapse.input not in seenNeurons:
               nextNeurons[synapse.input.id] = synapse.input
               if synapse.input.id in errors:
                  errors[synapse.input.id] += delta * synapse.weight
               else:
                  errors[synapse.input.id] = delta * synapse.weight


      for id, error in errors.iteritems():
         nextDeltas[id] = Activation.dactivate(nextNeurons[id].output, Configuration.sigmoidSlope, Configuration.sigmoidConstant) * error

      if len(nextNeurons) > 0:
         self.__propagate(nextNeurons.values(), nextDeltas, learningRate, seenNeurons)

      for neuron in neurons:
         for synapse in neuron.synapses:
            if synapse.input is not None:
               synapse.weight += learningRate * deltas[neuron.id] * synapse.input.output

   def dump(self, fileName):
      file = open(fileName, 'w')
      self.rdump(file, self.outputs)
      file.close()

   def rdump(self, file, neurons, usedIds=[]):
      nextNeurons = []
      for neuron in neurons:
         if neuron.id not in usedIds:
            usedIds.append(neuron.id)
            for synapse in neuron.synapses:
               line = repr(synapse.input.id) + ' ' + repr(neuron.id) + ' ' + repr(synapse.weight)
               file.write(line + '\n')
               nextNeurons.append(synapse.input)

      if len(nextNeurons) > 0:
         self.rdump(file, nextNeurons, usedIds)

   def load(self, fileName):
      file = open(fileName)

      self.inputs     = []
      self.outputs    = []
      self.allNeurons = []
      self.genotype   = None

      neurons  = {}
      inputIds = []

      for line in file:
         line   = line.strip()
         pieces = line.split()
         inId   = int(pieces[0])
         outId  = int(pieces[1])
         weight = float(pieces[2])

         input  = None
         output = None

         inputIds.append(inId)

         if inId not in neurons:
            input = Neuron(inId)
            neurons[inId] = input
            self.allNeurons.append(input)
         else:
            input = neurons[inId]

         if outId not in neurons:
            output = Neuron(outId)
            neurons[outId] = output
            self.allNeurons.append(output)
         else:
            output = neurons[outId]

         Synapse(input, output, weight)

      file.close()

      inputIds = set(inputIds)

      for neuron in self.allNeurons:
         if len(neuron.synapses) == 0:
            neuron.type = Neuron.INPUT
            self.inputs.append(neuron)
         elif neuron.id not in inputIds:
            neuron.type = Neuron.OUTPUT
            self.outputs.append(neuron)
