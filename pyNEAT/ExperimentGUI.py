graphicsAvailable = True
try:
   import Tkinter
except:
   graphicsAvailable = False

class ExperimentConsoleGUI:
   def __init__(self):
      pass

   def setRun(self, run):
      print 'Run:', run

   def setGeneration(self, generation):
      print 'Generation:', generation

   def setGenerationTime(self, time):
      print 'Time:', time

   def setHighestFitness(self, fitness):
      print 'Highest fitness:', fitness

   def winnerFound(self):
      print 'Found winner'

   def displayNetwork(self, network, showWeights):
      print 'Network', network.id
      for neuron in network.allNeurons:
         for synapse in neuron.synapses:
            if showWeights:
               print '\t', synapse.input.id, '-(', synapse.weight, ')->', neuron.id
            else:
               print '\t', synapse.input.id, '->', neuron.id

   def displayOutputs(self, targets, outputs):
      for i in range(len(targets)):
         print '\t', outputs[i], '->', targets[i]

   def startTest(self, name):
      print 'START TEST:', name

   def endTest(self, name):
      print 'END TEST:', name

if graphicsAvailable:
   class ExperimentGraphicsGUI:
      pass

   #ExperimentGUI = ExperimentGraphicsGUI
   ExperimentGUI = ExperimentConsoleGUI
else:
   ExperimentGUI = ExperimentConsoleGUI
