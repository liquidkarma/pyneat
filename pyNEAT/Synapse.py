import random

class Synapse:
   def __init__(self, input, output, weight, recurrent = False, trait = None):
      self.input     = input
      self.output    = output
      self.weight    = weight
      self.recurrent = recurrent
      self.trait     = trait
      self.enabled   = True

      if output is not None:
         self.output.synapses.append(self)

   def deriveTrait(self, trait):
      self.params = trait.params

   def perturb(self, sigma=0.75):
      self.weight += random.gauss(0.0, sigma)
