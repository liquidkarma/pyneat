graphicsAvailable = True
try:
   import Tkinter
   import tkMessageBox
   import tkFileDialog
   import tkSimpleDialog
except:
   graphicsAvailable = False

class ExperimentConsoleUI:
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

   def run(self):
      raise NotImplementedError, 'This UI is not interactive'

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

      def _makeLabel(self, text):
         label = Tkinter.Label(self, text=text, bd=1, relief=Tkinter.SUNKEN, anchor=Tkinter.W)
         label.pack(side=Tkinter.LEFT)
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

   class MyDialog(tkSimpleDialog.Dialog):
      def body(self, master):
         Tkinter.Label(master, text='First:').grid(row=0, sticky=Tkinter.W)
         Tkinter.Label(master, text='Second:').grid(row=1, sticky=Tkinter.W)

         self.e1 = Tkinter.Entry(master)
         self.e2 = Tkinter.Entry(master)

         self.e1.grid(row=0, column=1)
         self.e2.grid(row=1, column=1)

         self.cb = Tkinter.Checkbutton(master, text='Hardcopy')
         self.cb.grid(row=2, columnspan=2, sticky=Tkinter.W)

         return self.e1

      def validate(self):
         try:
            self.first  = int(self.e1.get())
            self.second = int(self.e2.get())
            return 1
         except ValueError:
            tkMessageBox.showerror('Bad Input', 'Illegal values, please try again')
            return 0

      def apply(self):
         self.result = self.first, self.second

   class ExperimentGUI:
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

         fileMenu.add_command(label='Open...', command=self.openNetwork)
         fileMenu.add_separator()
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
            self.running = True
            self.runButton.config(text='Stop')
            self.thread = threading.Thread(target=self.experiment.run)
            self.thread.start()
         else:
            self.running = False
            self.runButton.config(text='Run')
            # TODO: actually stop the experiment

      def setRun(self, run):
         self.status.setRun(run)

      def setGeneration(self, generation):
         self.status.setGeneration(generation)

      def setGenerationTime(self, time):
         self.status.setGenerationTime(time)

      def setHighestFitness(self, fitness):
         self.status.setHighestFitness(fitness)

      def winnerFound(self):
         #tkMessageBox.showinfo('Winner', 'Found winner')
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
         self.outputList.delete(0, Tkinter.END)
         for i in range(len(targets)):
            self.outputList.insert(Tkinter.END, (outputs[i], '->', targets[i]))

      def startTest(self, name):
         self.status.setRunning(True)

      def endTest(self, name):
         self.status.setRunning(False)

      def run(self):
         #self.experiment.run()
         self.root.mainloop()

   ExperimentUI = ExperimentGUI
   #ExperimentUI = ExperimentConsoleUI
else:
   ExperimentUI = ExperimentConsoleUI
