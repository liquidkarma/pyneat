graphicsAvailable = True
try:
   import Tkinter
   import tkMessageBox
   import tkFileDialog
   import tkSimpleDialog
except:
   graphicsAvailable = False

class ExperimentUIBase:
   def run(self):
      self.running = True

      self.startTest(self.experiment.name)

      for run in self.experiment.getRuns():
         if not self.running:
            print 'Experiment terminated'
            break
         else:
            self.setRun(run.id)
            self.setGeneration(run.generation)
            self.setWinner(run.winner)
            self.setHighestFitness(run.fitness)
            self.setGenerationTime(run.time)
            self.displayNetwork(run.champion, True)
            self.displayOutputs(run.targets, run.outputs)

      self.endTest(self.experiment.name)

class ExperimentConsoleUI(ExperimentUIBase):
   def __init__(self, experiment):
      self.experiment = experiment

   def setRun(self, run):
      print 'Run:', run

   def setGeneration(self, generation):
      print 'Generation:', generation

   def setGenerationTime(self, time):
      print 'Time:', time

   def setHighestFitness(self, fitness):
      print 'Highest fitness:', fitness

   def setWinner(self, winner):
      print 'Found winner:', winner

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
   import threading

   class StatusBar(Tkinter.Frame):
      def __init__(self, master):
         Tkinter.Frame.__init__(self, master)

         self.runningLabel        = self._makeLabel('Stopped')
         self.runLabel            = self._makeLabel('Run:')
         self.generationLabel     = self._makeLabel('Generation:')
         self.generationTimeLabel = self._makeLabel('Time:')
         self.highestFitness      = self._makeLabel('Highest fitness:')
         self.winner              = self._makeLabel('Winner:')

      def _makeLabel(self, text):
         label = Tkinter.Label(self, text=text, bd=1, relief=Tkinter.SUNKEN, anchor=Tkinter.W)
         label.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
         return label

      def _setLabel(self, label, text):
         label.config(text=text)
         label.update_idletasks()

      def setRunning(self, running):
         if running:
            self._setLabel(self.runningLabel, 'Running')
         else:
            self._setLabel(self.runningLabel, 'Stopped')

      def setRun(self, run):
         self._setLabel(self.runLabel, 'Run: %d' % run)

      def setGeneration(self, generation):
         self._setLabel(self.generationLabel, 'Generation: %d' % generation)

      def setGenerationTime(self, time):
         self._setLabel(self.generationTimeLabel, 'Time: %f' % time)

      def setHighestFitness(self, fitness):
         self._setLabel(self.highestFitness, 'Highest fitness: %f' % fitness)

      def setWinner(self, winner):
         if winner is not None:
            self._setLabel(self.winner, 'Winner: %d' % winner)
         else:
            self._setLabel(self.winner, 'Winner: None')

   class ExperimentGUI(ExperimentUIBase):
      def __init__(self, experiment):
         self.experiment = experiment
         self.running    = False

         self.root = Tkinter.Tk()

         self.root.title('pyNEAT')
         self.root.geometry('800x600')

         self._addMenus()
         self._addToolBar()
         self._addCanvas()
         self._addStatusBar()

      def _addMenus(self):
         menu = Tkinter.Menu(self.root)
         self.root.config(menu=menu)

         fileMenu = Tkinter.Menu(menu)
         menu.add_cascade(label='File', menu=fileMenu)

         #fileMenu.add_command(label='Open...', command=self.openNetwork)
         #fileMenu.add_separator()
         fileMenu.add_command(label='Exit', command=self.root.quit)

         helpMenu = Tkinter.Menu(menu)
         menu.add_cascade(label='Help', menu=helpMenu)
         helpMenu.add_command(label='About...', command=self.showAbout)

      def _addToolBar(self):
         self.toolbar = Tkinter.Frame(self.root)

         self.runButton = Tkinter.Button(self.toolbar, text='Run', width=6, command=self.doRun)
         self.runButton.pack(side=Tkinter.LEFT, padx=2, pady=2)

         self.toolbar.pack(side=Tkinter.TOP, fill=Tkinter.X)

      def _addCanvas(self):
         frame = Tkinter.Frame(self.root)
         frame.pack(fill=Tkinter.BOTH, expand=1)

         self.canvas = Tkinter.Canvas(frame, bg='blue')
         self.canvas.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)

         outputFrame = Tkinter.Frame(frame)
         outputFrame.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH, expand=1)

         self.outputVScroll = Tkinter.Scrollbar(outputFrame, orient=Tkinter.VERTICAL)
         self.outputHScroll = Tkinter.Scrollbar(outputFrame, orient=Tkinter.HORIZONTAL)
         self.outputList    = Tkinter.Listbox(outputFrame, xscrollcommand=self.outputHScroll.set, yscrollcommand=self.outputVScroll.set)
         self.outputVScroll.config(command=self.outputList.yview)
         self.outputHScroll.config(command=self.outputList.xview)
         self.outputVScroll.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
         self.outputHScroll.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
         self.outputList.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)

      def _addStatusBar(self):
         self.status = StatusBar(self.root)
         self.status.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)

      def openNetwork(self):
         file = tkFileDialog.askopenfilename()
         if file:
            print 'opening network', file

      def showAbout(self):
         tkMessageBox.showinfo('About', 'pyNEAT by Brian Greer\nBased on the NEAT algorithm by Ken Stanley')

      def openCallback(self):
         file = tkFileDialog.askopenfilename()
         if file:
            print 'opening', file

      def saveCallback(self):
         file = tkFileDialog.asksaveasfilename()
         if file:
            print 'saving as', file

      def doRun(self):
         if not self.running:
            self.runButton.config(text='Stop')
            #ExperimentUIBase.run(self)
            self.thread = threading.Thread(target=ExperimentUIBase.run, args=(self,))
            self.thread.start()
         else:
            self.running = False
            self.runButton.config(text='Stopping', state=Tkinter.DISABLED)

      def setRun(self, run):
         self.status.setRun(run)

      def setGeneration(self, generation):
         self.status.setGeneration(generation)

      def setGenerationTime(self, time):
         self.status.setGenerationTime(time)

      def setHighestFitness(self, fitness):
         self.status.setHighestFitness(fitness)

      def setWinner(self, winner):
         self.status.setWinner(winner)

      def getMaxDepth(self, synapse):
         depth = 0
         if synapse.input:
            maxDepth = 0
            for synapse in synapse.input.synapses:
               parentDepth = self.getMaxDepth(synapse)
               if parentDepth > maxDepth:
                  maxDepth = parentDepth
            depth = maxDepth + 1

         return depth

      def displayNetwork(self, network, showWeights):
         self.canvas.delete(Tkinter.ALL)

         canvasWidth  = self.canvas.winfo_width()
         canvasHeight = self.canvas.winfo_height()

         neurons     = {}
         connections = []
         for neuron in network.allNeurons:
            depth = 0 # neuron.getMaxDepth(0)
            for synapse in neuron.synapses:
               connections.append((synapse.input.id, synapse.weight, neuron.id))
               thisDepth = self.getMaxDepth(synapse)
               if thisDepth > depth:
                  depth = thisDepth
            if depth not in neurons:
               neurons[depth] = []
            # cull disconnected neurons
            if depth > 0 or (depth == 0 and neuron in network.inputs):
               neurons[depth].append(neuron.id)

         numLayers = len(neurons)

         maxLength = 0
         for depth, ids in neurons.iteritems():
            if len(ids) > maxLength:
               maxLength = len(ids)

         #neuronDiameter = canvasWidth / maxLength
         neuronDiameter = canvasHeight / (numLayers + numLayers - 1)

         coords = {}
         yDelta = canvasHeight / numLayers
         y      = canvasHeight - (yDelta + neuronDiameter) / 2
         for depth, ids, in neurons.iteritems():
            ids.sort()
            xDelta = canvasWidth / len(ids)
            x      = (xDelta - neuronDiameter) / 2;
            for id in ids:
               coords[id] = (x + neuronDiameter / 2, y)
               self.canvas.create_oval(x, y, x + neuronDiameter - 1, y + neuronDiameter - 1, fill='red')
               self.canvas.create_text(x + neuronDiameter / 2, y + neuronDiameter / 2, text=id)
               x += xDelta
            y -= yDelta

         usedConnections = {}
         for inputId, weight, outputId in connections:
            x0, y0 = coords[inputId]
            x1, y1 = coords[outputId]

            y1 += neuronDiameter

            width = 5
            if weight > 0:
               stipple = ''
               #width   = int(abs(2 * weight))
            else:
               stipple = 'gray25'
               #width   = 3

            if (inputId, outputId) in usedConnections:
               count = usedConnections[(inputId, outputId)]
               usedConnections[(inputId, outputId)] += 1
               xi = (x0 + x1) / 2 + (width + width) * (-1 ** count);
               yi = (y0 + y1) / 2 + (width + width) * (-1 ** count);
               self.canvas.create_line(x0, y0, xi, yi, x1, y1, width=width, stipple=stipple, smooth=True)
            else:
               self.canvas.create_line(x0, y0, x1, y1, width=width, stipple=stipple)
               usedConnections[(inputId, outputId)] = 1

         print 'Network', network.id
         for neuron in network.allNeurons:
            for synapse in neuron.synapses:
               if showWeights:
                  print '\t', synapse.input.id, '-(', synapse.weight, ')->', neuron.id
               else:
                  print '\t', synapse.input.id, '->', neuron.id

      def displayOutputs(self, targets, outputs):
         self.outputList.delete(0, Tkinter.END)
         for i in range(len(targets)):
            self.outputList.insert(Tkinter.END, (outputs[i], '->', targets[i]))

      def startTest(self, name):
         self.status.setRunning(True)

      def endTest(self, name):
         self.status.setRunning(False)
         self.runButton.config(text='Run', state=Tkinter.ACTIVE)

      def run(self):
         self.root.mainloop()

   ExperimentUI = ExperimentGUI
   #ExperimentUI = ExperimentConsoleUI
else:
   ExperimentUI = ExperimentConsoleUI
