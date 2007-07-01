from Configuration import *
from random_utils  import *

class Trait:
   def __init__(self, id=-1, t1=None, t2=None, config=None):
      self.id     = id
      self.params = []

      if t1 is not None and t2 is not None:
         self.id = t1.id
         for i in range(Configuration.numTraitParams):
            self.params.append((t1.params[i] + t2.params[i]) / 2.0)
      elif config is not None:
         self.id = int(config.pop(0))
         for param in config:
            self.params.append(float(param))
         deltaParams = Configuration.numTraitParams - len(config)
         if deltaParams > 0:
            for i in range(deltaParams):
               self.params.append(0)
         elif deltaParams < 0:
            self.params = self.params[:Configuration.numTraitPrams]
      else:
         for i in range(Configuration.numTraitParams):
            self.params.append(0)

   def mutate(self):
      for param in self.params:
         if randfloat() > Configuration.traitParamMutationProbability:
            param += randposneg() * randfloat() * Configuration.traitMutationPower
            if param < 0:
               param = 0
