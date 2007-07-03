from Synapse import *

class Gene:
   def __init__(self, input=None, output=None, weight=0.0, recurrent=False, trait=None, enabled=True, mutation=0.0, innovation=0.0):
      if input is None or output is None:
         raise ValueError

      self.input      = input
      self.output     = output
      self.synapse    = Synapse(input, output, weight, recurrent, trait)
      self.enabled    = enabled
      self.mutation   = mutation
      self.innovation = innovation
