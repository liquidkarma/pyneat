import math
import random

from Configuration import *
from Mutator       import *
from random_utils  import *
from Trait         import *
from Gene          import *
from Neuron        import *
from Synapse       import *
from NeuralNetwork import *
from Crossover     import *
from Innovation    import *

class Genome:
   def __init__(self, id=-1, neurons=None, genes=None, traits=None, fileName=None):
      self.id        = id
      self.phenotype = None

      if neurons is not None:
         self.neurons = list(neurons)
      else:
         self.neurons = []

      if genes is not None:
         self.genes = list(genes)
      else:
         self.genes = []

      if traits is not None:
         self.traits = list(traits)
      else:
         self.traits = []

      if fileName is not None:
         file = open(fileName)
         self.load(file)
         file.close()

   def load(self, file):
      for line in file.readlines():
         if not line.startswith('/*'):
            pieces = line.split()
            type   = pieces.pop(0)
            if type == 'genomestart':
               self.id = int(pieces[0])
            elif type == 'genomeend':
               if self.id != int(pieces[0]):
                  print "ERROR: id mismatch in genome specification"
                  break
            elif type == 'trait':
               self.traits.append(Trait(config=pieces))
            elif type == 'node':
               id      = int(pieces[0])
               traitId = int(pieces[1])
               type    = int(pieces[2])
               type    = int(pieces[3])

               found = False
               for trait in self.traits:
                  if trait.id == traitId:
                     found = True
                     self.neurons.append(Neuron(id, type, trait=trait))
                     break

               if not found:
                  self.neurons.append(Neuron(id, type))
            elif type == 'gene':
               traitId    = int(pieces[0])
               inputId    = int(pieces[1])
               outputId   = int(pieces[2])
               weight     = float(pieces[3])
               recurrent  = int(pieces[4])
               innovation = int(pieces[5])
               mutation   = int(pieces[6])
               enabled    = int(pieces[7])

               if recurrent == 1:
                  recurrent = True
               else:
                  recurrent = False

               if enabled == 1:
                  enabled = True
               else:
                  enabled = False

               trait  = None
               input  = None
               output = None

               for t in self.traits:
                  if t.id == traitId:
                     trait = t
                     break

               for neuron in self.neurons:
                  if neuron.id == inputId:
                     input = neuron
                  elif neuron.id == outputId:
                     output = neuron
                  if input is not None and output is not None:
                     break

               if trait is not None and input is not None and output is not None:
                  self.genes.append(Gene(input, output, weight, recurrent, trait, enabled, mutation, innovation))

   def dump(self, fileName):
      file = open(fileName, 'w')

      file.write('genomestart ' + str(self.id) + '\n')

      for trait in self.traits:
         file.write('trait ' + str(trait.id) + ' ' + \
                    ' '.join([str(x) for x in trait.params]) + \
                    '\n')

      for neuron in self.neurons:
         type = str(neuron.type)
         file.write('node ' + str(neuron.id) + \
                    ' ' + str(neuron.trait.id) + \
                    ' ' + type + \
                    ' ' + type + \
                    '\n')

      for gene in self.genes:
         recurrent = '0'
         if gene.recurrent:
            recurrent = '1'

         enabled = '1'
         if not gene.enabled:
            enabled = '0'

         file.write('gene ' + str(gene.trait.id) + \
                    ' ' + str(gene.input.id) + \
                    ' ' + str(gene.output.id) + \
                    ' ' + str(gene.synapse.weight) + \
                    ' ' + recurrent + \
                    ' ' + str(gene.innovation) + \
                    ' ' + str(gene.mutation) + \
                    ' ' + enabled)

      file.write('genomeend ' + str(self.id) + '\n')

      file.close()

   def genesis(self, id):
      inputs  = []
      outputs = []
      all     = []

      for neuron in self.neurons:
         newNeuron = Neuron(neuron.id, neuron.type)

         if neuron.type == Neuron.INPUT or neuron.type == Neuron.BIAS:
            inputs.append(newNeuron)
         elif neuron.type == Neuron.OUTPUT:
            outputs.append(newNeuron)

         all.append(newNeuron)

         neuron.analogue = newNeuron

      for gene in self.genes:
         if gene.enabled:
            input   = gene.synapse.input.analogue
            output  = gene.synapse.output.analogue
            synapse = Synapse(input, output, gene.synapse.weight, gene.synapse.recurrent)

      newNetwork = NeuralNetwork(id, inputs, outputs, all)

      newNetwork.genotype = self
      self.phenotype      = newNetwork

      return newNetwork

   def getCompatibility(self, genome):
      numExcess               = 0
      numMatching             = 0
      numDisjoint             = 0
      totalMutationDifference = 0

      numGenes      = len(self.genes)
      numOtherGenes = len(genome.genes)

      i, j = 0, 0

      while i < numGenes or j < numOtherGenes:
         if i == numGenes:
            numExcess += numOtherGenes - j
            break
         elif j == numOtherGenes:
            numExcess += numGenes - i
            break
         else:
            myInnovation    = self.genes[i].innovation
            otherInnovation = genome.genes[j].innovation

            if myInnovation == otherInnovation:
               numMatching += 1
               totalMutationDifference += math.fabs(self.genes[i].mutation - genome.genes[j].mutation)
               i += 1
               j += 1
            elif myInnovation < otherInnovation:
               i += 1
               numDisjoint += 1
            elif otherInnovation < myInnovation:
               j += 1
               numDisjoint += 1

      return Configuration.disjointCoefficient           * (numDisjoint / 1.0) + \
             Configuration.excessCoefficient             * (numExcess   / 1.0) + \
             Configuration.mutationDifferenceCoefficient * (totalMutationDifference / numMatching)

   def isCompatibleWith(self, genome):
      return self.getCompatibility(genome) < Configuration.compatibilityThreshold

   def tryAllMutations(self, mutationPower):
      if randfloat() < Configuration.mutateRandomTraitProbability:
         self.mutateRandomTrait()

      if randfloat() < Configuration.mutateSynapseTraitProbability:
         self.mutateSynapseTrait(1)

      if randfloat() < Configuration.mutateNeuronTraitProbability:
         self.mutateNeuronTrait(1)

      if randfloat() < Configuration.mutateSynapseWeightsProbability:
         self.mutateSynapseWeights(Mutator.GAUSSIAN, mutationPower, 1.0)

      if randfloat() < Configuration.mutateToggleEnableProbability:
         self.mutateToggleEnable(1)

      if randfloat() < Configuration.mutateGeneReenableProbability:
         self.mutateGeneReenable()

   def mutateRandomTrait(self):
      if len(self.traits) > 0:
         index = random.randint(0, len(self.traits) - 1)
         self.traits[index].mutate()

   def mutateSynapseTrait(self, times):
      if len(self.traits) > 0 and len(self.genes) > 0:
         for i in range(times):
            traitIndex = random.randint(0, len(self.traits) - 1)
            geneIndex  = random.randint(0, len(self.genes) - 1)

            self.genes[geneIndex].synapse.trait = self.traits[traitIndex]

   def mutateNeuronTrait(self, times):
      if len(self.traits) > 0 and len(self.neurons) > 0:
         for i in range(times):
            traitIndex  = random.randint(0, len(self.traits) - 1)
            neuronIndex = random.randint(0, len(self.neurons) - 1)

            self.neurons[neuronIndex].trait = self.traits[traitIndex]

   def mutateSynapseWeights(self, type, power, rate):
      severe = False
      if randfloat() > 0.5:
         severe = True

      index    = 0.0
      numGenes = len(self.genes)
      endPart  = numGenes * 0.8
      powermod = 1.0

      for gene in self.genes:
         gausspoint     = 0.0
         coldgausspoint = 0.0

         if severe:
            gausspoint     = 0.3
            coldgausspoint = 0.1
         elif numGenes >= 10 and index > endPart:
            gausspoint     = 0.5
            coldgausspoint = 0.3
         else:
            # half of the time don't do any cold mutations
            if randfloat() > 0.5:
               gausspoint    = 1.0 - rate
               colgausspoint = 1.0 - rate - 0.1
            else:
               gausspoint    = 1.0 - rate
               colgausspoint = 1.0 - rate - 0.1

         value = randposneg() * randfloat() * power * powermod

         if type == Mutator.GAUSSIAN:
            choice = randfloat()
            if choice > gausspoint:
               gene.synapse.weight += value
            elif choice > coldgausspoint:
               gene.synapse.weight = value
         elif type == Mutator.COLDGAUSSIAN:
            gene.synapse.weight = value

         gene.mutation = gene.synapse.weight

         index += 1.0

   def mutateToggleEnable(self, times):
      if len(self.genes) > 0:
         for i in range(times):
            index      = random.randint(0, len(self.genes) - 1)
            mutateGene = self.genes[index]

            if mutateGene.enabled:
               # make sure we don't isolate a neuron by disabling this gene
               valid = False
               for gene in self.genes:
                  if mutateGene.input == gene.input and gene.enabled and mutateGene.innovation != gene.innovation:
                     valid = True
                     break
               if valid:
                  mutateGene.enabled = False
            else:
               mutateGene.enabled = True

   # Find first disabled gene and enable it
   def mutateGeneReenable(self):
      for gene in self.genes:
         if not gene.enabled:
            gene.enabled = True
            break

   def mutateAddNeuron(self, id, currentInnovation, innovations):
      splitGene = None

      if len(self.genes) < 15:
         checking = False
         for gene in self.genes:
            if checking:
               if randfloat() < 0.3:
                  splitGene = gene
                  break
            elif gene.enabled and gene.synapse.input.type != Neuron.BIAS:
               checking = True
      else:
         tryCount = 0
         while tryCount < 20 and splitGene is None:
            index = random.randint(0, len(self.genes) - 1)
            if self.genes[index].enabled and self.genes[index].synapse.input.type != Neuron.BIAS:
               splitGene = self.genes[index]
               break
            tryCount += 1

      if splitGene is not None:
         splitGene.enabled = False

         synapse   = splitGene.synapse
         oldWeight = synapse.weight
         input     = synapse.input
         output    = synapse.output

         newGene1  = None
         newGene2  = None
         newNeuron = None

         found = False
         for innovation in innovations:
            if innovation.type == Innovation.NEURON and \
               innovation.inId == input.id and \
               innovation.outId == output.id and \
               innovation.oldId == splitGene.innovation:
               newNeuron = Neuron(innovation.newNeuronId)

               if len(self.traits) > 0:
                  newNeuron.trait = self.traits[0]

               newGene1 = Gene(input, newNeuron, 1.0, synapse.recurrent, synapse.trait, innovation=innovation.idA, mutation=0)
               newGene2 = Gene(newNeuron, output, oldWeight, False, synapse.trait, innovation=innovation.idB, mutation=0)

               found = True
               break


         if not found:
            newNeuron = Neuron(id)
            id += 1

            if len(self.traits) > 0:
               newNeuron.trait = self.traits[0]

            newGene1 = Gene(input, newNeuron, 1.0, synapse.recurrent, synapse.trait, innovation=currentInnovation, mutation=0)
            newGene2 = Gene(newNeuron, output, oldWeight, False, synapse.trait, innovation=currentInnovation + 1, mutation=0)

            innovations.append(Innovation(input.id, output.id, idA=currentInnovation, idB=currentInnovation + 1.0, oldId=splitGene.innovation, type=Innovation.NEURON, newNeuronId=newNeuron.id))

            currentInnovation += 2.0

         if newNeuron is not None:
            self.genes.append(newGene1)
            self.genes.append(newGene2)
            self.neurons.append(newNeuron)

   def mutateAddSynapse(self, currentInnovation, innovations, tries):
      recurrent = False
      if randfloat() < Configuration.recurrentProbability:
         recurrent = True

      startIndex = 0
      for neuron in self.neurons:
         if neuron.type != Neuron.INPUT:
            break
         else:
            startIndex += 1

      numNeurons = len(self.neurons)

      threshold  = numNeurons * numNeurons

      found = False
      count = 0

      input  = None
      output = None

      if recurrent:
         while count < tries:
            inputIndex  = 0
            outputIndex = 0

            # random recurrency
            if randfloat() > 0.5:
               inputIndex  = random.randint(startIndex, numNeurons - 1)
               outputIndex = inputIndex
            else:
               inputIndex  = random.randint(0, numNeurons - 1)
               outputIndex = random.randint(startIndex, numNeurons - 1)

            input  = self.neurons[inputIndex]
            output = self.neurons[outputIndex]

            if output.type != Neuron.INPUT and self.phenotype.isRecurrent(input.analogue, output.analogue, 0, threshold):
               for gene in self.genes:
                  if gene.synapse.input == input and gene.synapse.output == output and gene.synapse.recurrent:
                     found = True
                     break

               if found:
                  break

            count += 1
      else:
         while count < tries:
            inputIndex  = random.randint(0, numNeurons - 1)
            outputIndex = random.randint(startIndex, numNeurons - 1)

            input  = self.neurons[inputIndex]
            output = self.neurons[outputIndex]

            if output.type != Neuron.INPUT and not self.phenotype.isRecurrent(input.analogue, output.analogue, 0, threshold):
               for gene in self.genes:
                  if gene.synapse.input == input and gene.synapse.output == output and not gene.synapse.recurrent:
                     found = True
                     break

               if found:
                  break

            count += 1

      if found:
         found = False

         newGene = None

         for innovation in innovations:
            if innovation.type == Innovation.SYNAPSE and innovation.inId == input.id and innovation.outId == output.id and innovation.recurrent == recurrent:
               newGene = Gene(input, output, innovation.weight, recurrent, self.traits[innovation.traitId], innovation=innovation.idA)
               found = True
               break

         if not found:
            traitIndex = random.randint(0, len(self.traits) - 1)
            newWeight  = randposneg() * randfloat() * 10.0
            newGene    = Gene(input, output, newWeight, recurrent, innovation=currentInnovation, mutation=newWeight)
            innovations.append(Innovation(inId=input.id, outId=output.id, weight=newWeight, idA=currentInnovation, traitId=traitIndex, type=Innovation.SYNAPSE, recurrent=recurrent))

         self.genes.append(newGene)

   def insertNeuron(self, neurons, newNeuron):
      inserted = False
      id       = newNeuron.id

      for i in range(len(neurons)):
         if neurons[i].id > id:
            neurons.insert(i, newNeuron)
            inserted = True
            break

      if not inserted:
         neurons.append(newNeuron)

   def addNeuron(self, referenceNeuron, neuronPool, traitPool):
      newNeuron = None
      found     = False

      for neuron in neuronPool:
         if neuron.id == referenceNeuron.id:
            newNeuron = neuron
            found     = True
            break

      if not found:
         if referenceNeuron.trait is None:
            newTraitId = 0
         else:
            newTraitId = referenceNeuron.trait.id - self.traits[0].id

         newNeuron       = Neuron(referenceNeuron.id, referenceNeuron.type, \
                                  referenceNeuron.synapses, referenceNeuron.output, \
                                  referenceNeuron.active)
         newNeuron.trait = traitPool[newTraitId]

         self.insertNeuron(neuronPool, newNeuron)

      return newNeuron

   def crossover(self, type, dad, id, momFitness=0, dadFitness=0):
      babyTraits = []
      for i in range(len(self.traits)):
         babyTraits.append(Trait(t1=self.traits[i], t2=dad.traits[i]))

      babyGenes   = []
      babyNeurons = []

      blxPos = randfloat()

      averageGene = Gene()

      momBetter = True
      if momFitness < dadFitness or (momFitness == dadFitness and len(dad.genes) < len(self.genes)):
         momBetter = False

      momIndex, dadIndex = 0, 0

      momStopIndex, dadStopIndex = len(self.genes), len(dad.genes)

      geneCounter    = 0
      crossoverPoint = 0

      momGenes = self.genes
      dadGenes = dad.genes

      if type == Crossover.SINGLEPOINT:
         if momStopIndex < dadStopIndex:
            crossoverPoint = random.randint(0, momStopIndex)
         else:
            crossoverPoint = random.randint(0, dadStopIndex)
            momGenes       = dad.genes
            momStopIndex   = dadStopIndex
            dadGenes       = self.genes
            dadStopIndex   = len(dadGenes)

      while momIndex < momStopIndex or dadIndex < dadStopIndex:
         skip       = False
         chosenGene = None
         disabled   = False

         averageGene.enabled = True

         if momIndex == momStopIndex:
            chosenGene = dadGenes[dadIndex]
            dadIndex += 1
            if type != Crossover.SINGLEPOINT and momBetter:
               skip = True
         elif dadIndex == dadStopIndex:
            chosenGene = momGenes[momIndex]
            momIndex += 1
            if type != Crossover.SINGLEPOINT and not momBetter:
               skip = True
         else:
            momGene       = momGenes[momIndex]
            dadGene       = dadGenes[dadIndex]

            momInnovation = momGene.innovation
            dadInnovation = dadGene.innovation

            if momInnovation == dadInnovation:
               if type == Crossover.MULTIPOINT:
                  if randfloat() < 0.5:
                     chosenGene = momGene
                  else:
                     chosenGene = dadGene

                  if not momGene.enabled or not dadGene.enabled:
                     if randfloat() < 0.75:
                        disabled = True
               else:
                  useAverage = True

                  if type == Crossover.SINGLEPOINT:
                     useAverage = False
                     if geneCounter < crossoverPoint:
                        chosenGene = momGene
                     elif geneCounter > crossoverPoint:
                        chosenGene = dadGene
                     else:
                        useAverage = True

                  if useAverage:
                     if randfloat() > 0.5:
                        averageGene.synapse.trait = momGene.synapse.trait
                     else:
                        averageGene.synapse.trait = dadGene.synapse.trait

                     if type == Crossover.BLX:
                        blxAlpha = -0.4
                        blxMax   = 0.0
                        blxMin   = 0.0

                        w1 = momGene.synapse.weight
                        w2 = dadGene.synapse.weight

                        if w1 > w2:
                           blxMax = w1
                           blxMin = w2
                        else:
                           blxMax = w2
                           blxMin = w1

                        blxRange   = blxMax - blxMin
                        blxExplore = blxAlpha * blxRange

                        blxMin -= blxExplore
                        blxMax += blxExplore

                        blxRange = blxMax - blxMin

                        averageGene.synapse.weight = blxMin + blxPos * blxRange
                     else:
                        averageGene.synapse.weight = (momGene.synapse.weight + dadGene.synapse.weight) / 2.0

                     if randfloat() > 0.5:
                        averageGene.synapse.input = momGene.synapse.input
                     else:
                        averageGene.synapse.input = dadGene.synapse.input

                     if randfloat() > 0.5:
                        averageGene.synapse.output = momGene.synapse.output
                     else:
                        averageGene.synapse.output = dadGene.synapse.output

                     if randfloat() > 0.5:
                        averageGene.synapse.recurrent = momGene.synapse.recurrent
                     else:
                        averageGene.synapse.recurrent = dadGene.synapse.recurrent

                     averageGene.innovation = momGene.innovation
                     averageGene.mutation   = (momGene.mutation + dadGene.mutation) / 2.0

                     if not momGene.enabled or not dadGene.enabled:
                        if randfloat() < 0.75:
                           averageGene.enabled = False

                     chosenGene = averageGene

               momIndex    += 1
               dadIndex    += 1
               geneCounter += 1

            elif momInnovation < dadInnovation:
               if type == Crossover.SINGLEPOINT:
                  if geneCounter < crossoverPoint:
                     chosenGene   = momGene
                     momIndex    += 1
                     geneCounter += 1
                  else:
                     chosenGene   = dadGene
                     dadIndex    += 1
               else:
                  chosenGene = momGene
                  momIndex += 1
                  if not momBetter:
                     skip = True
            elif dadInnovation < momInnovation:
               if type == Crossover.SINGLEPOINT:
                  dadIndex += 1
                  skip = True
               else:
                  chosenGene = dadGene
                  dadIndex += 1
                  if momBetter:
                     skip = True

         for gene in babyGenes:
            if gene.synapse.input.id == chosenGene.synapse.input.id   and \
               gene.synapse.output.id == chosenGene.synapse.output.id and \
               (gene.synapse.recurrent == chosenGene.synapse.recurrent or \
                gene.synapse.recurrent or chosenGene.synapse.recurrent):
               skip = True
               break

         if not skip:
            traitId   = 0
            newInput  = None
            newOutput = None

            if chosenGene.synapse.trait is None:
               traitId = self.traits[0].id
            else:
               traitId = chosenGene.synapse.trait.id - self.traits[0].id

            input  = chosenGene.synapse.input
            output = chosenGene.synapse.output

            if input.id < output.id:
               newInput  = self.addNeuron(input , babyNeurons, babyTraits)
               newOutput = self.addNeuron(output, babyNeurons, babyTraits)
            else:
               newOutput = self.addNeuron(output, babyNeurons, babyTraits)
               newInput  = self.addNeuron(input , babyNeurons, babyTraits)

            newGene = Gene(chosenGene.input, chosenGene.output, enabled=chosenGene.enabled, \
                           mutation=chosenGene.mutation, innovation=chosenGene.innovation)
            newGene.synapse = Synapse(newInput, newOutput, \
                                      chosenGene.synapse.weight, chosenGene.synapse.recurrent, \
                                      babyTraits[traitId])

            if disabled:
               newGene.enabled = False
               disabled = False

            babyGenes.append(newGene)

      return Genome(id, babyNeurons, babyGenes, babyTraits)

   def getLastNeuronId(self):
      if len(self.neurons) > 0:
         return self.neurons[-1].id + 1
      else:
         return -1

   def getLastGeneInnovationId(self):
      if len(self.genes):
         return self.genes[-1].innovation + 1
      else:
         return -1
