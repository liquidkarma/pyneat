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

graphicsAvailable = True
try:
   import Tkinter
   import tkMessageBox
   import tkFileDialog
   import tkSimpleDialog
except:
   graphicsAvailable = False

from Configuration import *

class ExperimentUIBase:
   def run(self):
      self.running = True

      self.startTest(self.experiment.name)

      for run in self.experiment.getRuns():
         self.handleRun(run)

         if not self.running:
            print 'Experiment terminated'
            break

      self.endTest(self.experiment.name)

      self.running = False

   def handleRun(self, run):
      self.setRun(run.id)
      self.setGeneration(run.generation)
      self.setWinner(run.winner)
      self.setHighestFitness(run.fitness)
      self.setGenerationTime(run.time)
      self.displayNetwork(run.champion, True)
      self.displayOutputs(run.targets, run.outputs)

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

   class ConfigDialog(tkSimpleDialog.Dialog):
      def body(self, master):
         self.title('Configuration Options')

         self.scroll = Tkinter.Scrollbar(master, orient=Tkinter.VERTICAL)
         self.scroll.grid(row=0, column=1, sticky=Tkinter.N+Tkinter.S)

         self.canvas = Tkinter.Canvas(master, yscrollcommand=self.scroll.set)
         self.canvas.grid(row=0, column=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)

         self.scroll.config(command=self.canvas.yview)

         master.grid_rowconfigure(0, weight=1)
         master.grid_columnconfigure(0, weight=1)

         self.frame = Tkinter.Frame(self.canvas)
         self.frame.rowconfigure(1, weight=1)
         self.frame.columnconfigure(1, weight=1)

         self.config = {}

         r = 0
         members = sorted(getConfigurationPairs().iteritems(), lambda x, y: cmp(x[0], y[0]))
         for name, value in members:
            Tkinter.Label(self.frame, text=name).grid(row=r, sticky=Tkinter.W)
            entry = Tkinter.Entry(self.frame)
            entry.insert(0, str(value))
            entry.grid(row=r, column=1)
            r += 1
            self.config[name] = entry

         self.canvas.create_window(0, 0, anchor=Tkinter.NW, window=self.frame)

         self.frame.update_idletasks()

         self.canvas.config(scrollregion=self.canvas.bbox('all'))

         return None

      def validate(self):
         try:
            for value in self.config.values():
               ival = float(value.get()) # generic test of validity
            return 1
         except ValueError:
            tkMessageBox.showerror('Bad Input', 'Illegal values, please try again')
            return 0

      def apply(self):
         config = {}
         for key, entry in self.config.iteritems():
            config[key] = entry.get()

         setConfiguration(config)

   class ExperimentGUI(ExperimentUIBase):
      def __init__(self, experiment):
         self.experiment = experiment
         self.running    = False
         self._run       = None
         self.lock       = threading.Lock()
         self.event      = threading.Event()

         self.root = Tkinter.Tk()

         self.root.title('pyNEAT')
         self.root.geometry('800x600')

         self._addMenus()
         self._addToolBar()
         self._addCanvas()
         self._addStatusBar()

         self.fitnesses = []

      def _addMenus(self):
         menu = Tkinter.Menu(self.root)
         self.root.config(menu=menu)

         fileMenu = Tkinter.Menu(menu)
         menu.add_cascade(label='File', menu=fileMenu)

         fileMenu.add_command(label='Set start genes file...', command=self.doStartGenes)
         fileMenu.add_separator()
         fileMenu.add_command(label='Options...'             , command=self.doOptions)
         fileMenu.add_command(label='Save Options...'        , command=self.doSaveOptions)
         #fileMenu.add_separator()
         #fileMenu.add_command(label='Open Network...'        , command=self.openNetwork)
         fileMenu.add_separator()
         fileMenu.add_command(label='Exit'                   , command=self.doQuit)

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

         self.netCanvas = Tkinter.Canvas(frame, bg='blue')
         self.netCanvas.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=1)

         self.fitnessCanvas = Tkinter.Canvas(frame, bg='black')
         self.fitnessCanvas.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)

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

      def doStartGenes(self):
         file = tkFileDialog.askopenfilename(initialfile=self.experiment.startGenesFileName)
         if file:
            print 'Setting start genes to file:', file
            self.experiment.startGenesFileName = file

      def doOptions(self):
         ConfigDialog(self.root)

      def doSaveOptions(self):
         file = tkFileDialog.asksaveasfilename()
         if file:
            print 'Saving configuration as', file
            printConfiguration(file)

      def openNetwork(self):
         file = tkFileDialog.askopenfilename()
         if file:
            print 'Opening network', file

      def showAbout(self):
         tkMessageBox.showinfo('About', 'pyNEAT by Brian Greer\nNEAT algorithm by Ken Stanley\nhttp://code.google.com/p/pyneat')

      def openCallback(self):
         file = tkFileDialog.askopenfilename()
         if file:
            print 'opening', file

      def saveCallback(self):
         file = tkFileDialog.asksaveasfilename()
         if file:
            print 'saving as', file

      def doQuit(self):
         self.running = False
         self.root.quit()

      def doRun(self):
         if not self.running:
            self.runButton.config(text='Stop')
            self.thread = threading.Thread(target=ExperimentUIBase.run, args=(self,))
            self.thread.start()
            self.root.after(10, self.update)
         else:
            self.running = False
            self.runButton.config(text='Stopping', state=Tkinter.DISABLED)

      def handleRun(self, run):
         if self.running:
            self.lock.acquire()
            self._run = run
            self.event.clear()
            self.lock.release()

            self.event.wait()

      def update(self):
         if self._run is not None:
            self.lock.acquire()
            ExperimentUIBase.handleRun(self, self._run)
            self._run = None
            self.event.set()
            self.lock.release()

         if self.running:
            self.root.after(10, self.update)

      def setRun(self, run):
         self.status.setRun(run)

      def setGeneration(self, generation):
         self.status.setGeneration(generation)

      def setGenerationTime(self, time):
         self.status.setGenerationTime(time)

      def setHighestFitness(self, fitness):
         self.status.setHighestFitness(fitness)

         self.fitnesses.append(fitness)

         self.fitnessCanvas.delete(Tkinter.ALL)

         fitnessCanvasWidth  = self.fitnessCanvas.winfo_width()
         fitnessCanvasHeight = self.fitnessCanvas.winfo_height()

         maxFitness = 0.0
         for fitness in self.fitnesses:
            if fitness > maxFitness:
               maxFitness = fitness

         maxFitness *= 2.0

         if maxFitness > 0:
            yFact = fitnessCanvasHeight / maxFitness
         else:
            yFact = 0

         numFitnessPoints = len(self.fitnesses)
         if numFitnessPoints < 50:
            numFitnessPoints = 60
         else:
            numFitnessPoints += 10

         xStep = fitnessCanvasWidth / numFitnessPoints

         x0 = 0
         y0 = fitnessCanvasHeight - 1
         for fitness in self.fitnesses:
            x1 = x0 + xStep
            y1 = fitnessCanvasHeight - fitness * yFact - 1
            self.fitnessCanvas.create_line(x0, y0, x1, y1, fill='red')
            x0 = x1
            y0 = y1

         self.netCanvas.update_idletasks()

      def setWinner(self, winner):
         self.status.setWinner(winner)

      def displayNetwork(self, network, showWeights):
         self.netCanvas.delete(Tkinter.ALL)

         netCanvasWidth  = self.netCanvas.winfo_width()
         netCanvasHeight = self.netCanvas.winfo_height()

         neurons     = {}
         connections = []
         for neuron in network.allNeurons:
            #layer = neuron.getMaxDepth()
            if neuron in network.inputs:
               layer = 0
            elif neuron in network.outputs:
               layer = 2
            else:
               layer = 1

            for synapse in neuron.synapses:
               connections.append((synapse.input.id, synapse.weight, neuron.id))
            if layer not in neurons:
               neurons[layer] = []
            neurons[layer].append(neuron.id)

         numLayers = len(neurons)

         maxLength = 0
         for ids in neurons.itervalues():
            if len(ids) > maxLength:
               maxLength = len(ids)

         if maxLength > numLayers:
            neuronDiameter = netCanvasHeight / (maxLength + maxLength - 1)
         else:
            neuronDiameter = netCanvasHeight / (numLayers + numLayers - 1)

         coords = {}
         yDelta = netCanvasHeight / numLayers
         y      = netCanvasHeight - (yDelta + neuronDiameter) / 2
         for ids in neurons.itervalues():
            ids.sort()
            xDelta = netCanvasWidth / len(ids)
            x      = (xDelta - neuronDiameter) / 2;
            for id in ids:
               coords[id] = (x + neuronDiameter / 2, y)
               self.netCanvas.create_oval(x, y, x + neuronDiameter - 1, y + neuronDiameter - 1, fill='red')
               self.netCanvas.create_text(x + neuronDiameter / 2, y + neuronDiameter / 2, text=id)
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

            if inputId == outputId:
               # TODO: handle recurrent connection drawing
               pass
            else:
               if (inputId, outputId) in usedConnections:
                  count = usedConnections[(inputId, outputId)]
                  usedConnections[(inputId, outputId)] += 1
                  xi = (x0 + x1) / 2 + (width + width) * (-1 ** count);
                  yi = (y0 + y1) / 2 + (width + width) * (-1 ** count);
                  self.netCanvas.create_line(x0, y0, xi, yi, x1, y1, width=width, stipple=stipple, smooth=True, arrow=Tkinter.LAST)
               else:
                  self.netCanvas.create_line(x0, y0, x1, y1, width=width, stipple=stipple, arrow=Tkinter.LAST)
                  usedConnections[(inputId, outputId)] = 1

               if weight > 0:
                  self.netCanvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text='%.4f' % weight, fill='white')

         self.netCanvas.update_idletasks()

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
         self.root.title('pyNEAT - ' + name)
         self.status.setRunning(True)
         self.fitnesses = []

      def endTest(self, name):
         self.status.setRunning(False)
         self.running = False
         self.runButton.config(text='Run', state=Tkinter.ACTIVE)

      def run(self):
         self.root.mainloop()

   ExperimentUI = ExperimentGUI
   #ExperimentUI = ExperimentConsoleUI
else:
   ExperimentUI = ExperimentConsoleUI
