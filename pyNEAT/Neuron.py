from Configuration import *

import Activation

class Neuron:
   HIDDEN = 0
   INPUT  = 1
   OUTPUT = 2
   BIAS   = 3

   def __init__(self, id=-1, type=HIDDEN, synapses=None, output=0.0, active=True, trait=None):
      self.id         = id
      self.type       = type
      self.input      = None
      self.output     = output
      self.active     = active
      self.analogue   = None
      self.trait      = trait
      self.activating = False

      if synapses is not None:
         self.synapses = list(synapses)
      else:
         self.synapses = []

   def __str__(self):
      return '<%d %f %f>' % (self.id, self.input, self.output)

   def __repr__(self):
      return '<' + str(self.id) + ' ' + str(self.input) + ' ' + str(self.output) + '>'

   def deriveTrait(self, trait):
      self.params = trait.params

   def activate(self, debug=False):
      if self.activating:
         return self.output
      else:
         self.activating = True

         output = 0.0

         if (self.type == Neuron.INPUT or self.type == Neuron.BIAS) and self.input is not None:
            output = self.input

         if debug:
            print 'Neuron', self.id, ',', self.type, ',', self.output

         for synapse in self.synapses:
            if synapse.enabled:
               if debug:
                  print '\tinput=', synapse.input.getOutput(),
               if synapse.input == self:
                  output += self.output * synapse.weight
               else:
                  output += synapse.input.getOutput() * synapse.weight

         if debug:
            print '\tpre-output:', output

         self.output = Activation.activate(output, Configuration.sigmoidSlope, Configuration.sigmoidConstant)

         if debug:
            print '\toutput=', self.output

         self.activating = False

         return self.output

   def getOutput(self):
      return self.activate()

   def getMaxDepth(self, currentDepth=0, seenNeurons=None):
      if seenNeurons is None:
         seenNeurons = [self]
      else:
         seenNeurons.append(self)

      maxDepth = currentDepth

      for synapse in self.synapses:
         if synapse.input not in seenNeurons:
            depth = synapse.input.getMaxDepth(currentDepth + 1, seenNeurons)
            if depth > maxDepth:
               maxDepth = depth

      return maxDepth

   def clear(self, seenNeurons=None):
      if seenNeurons is None:
         seenNeurons = [self]
      else:
         seenNeurons.append(self)

      if self.type != Neuron.INPUT:
         self.output = 0.0
         for synapse in self.synapses:
            if synapse.input not in seenNeurons:
               synapse.input.clear(seenNeurons)
