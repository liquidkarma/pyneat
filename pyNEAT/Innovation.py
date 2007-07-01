class Innovation:
   NEURON  = 0
   SYNAPSE = 1

   def __init__(self, inId, outId, weight = 0.0, traitId = -1, oldId = -1, recurrent = False, type=NEURON, idA = -1, idB = -1, newNeuronId = -1):
      self.inId        = inId
      self.outId       = outId
      self.weight      = weight
      self.traitId     = traitId
      self.oldId       = oldId
      self.recurrent   = recurrent
      self.type        = type
      self.idA         = idA
      self.idB         = idB
      self.newNeuronId = newNeuronId
