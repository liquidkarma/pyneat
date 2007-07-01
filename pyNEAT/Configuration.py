import inspect

class Configuration:
   numTraitParams = 8

   traitParamMutationProbability = 0.5 # Prob. of mutating a single trait param
   traitMutationPower            = 1.0 # Power of mutation on a signle trait param

   # Amount that mutation_num changes for a trait change inside a link
   linktrait_mut_sig = 1.0

   # Amount a mutation_num changes on a link connecting a node that changed its trait
   nodetrait_mut_sig = 0.5

   weightMutationPower = 1.8 # The power of a linkweight mutation

   # These 3 global coefficients are used to determine the formula for
   # computating the compatibility between 2 genomes.  The formula is:
   # disjoint_coeff*pdg+excess_coeff*peg+mutdiff_coeff*mdmg.
   # See the compatibility method in the Genome class for more info
   # They can be thought of as the importance of disjoint Genes,
   # excess Genes, and parametric difference between Genes of the
   # same function, respectively.
   disjointCoefficient           = 1.0
   excessCoefficient             = 1.0
   mutationDifferenceCoefficient = 3.0

   # This global tells compatibility threshold under which
   # two Genomes are considered the same species
   compatibilityThreshold = 4.0

   # Globals involved in the epoch cycle - mating, reproduction, etc..
   ageSignificance                 = 1.0  # How much does age matter?
   survivalThreshold               = 0.4  # Percent of ave fitness for survival
   mutateOnlyProbability           = 0.25 # Prob. of a non-mating reproduction
   mutateRandomTraitProbability    = 0.1
   mutateSynapseTraitProbability   = 0.1
   mutateNeuronTraitProbability    = 0.1
   mutateSynapseWeightsProbability = 0.8
   mutateToggleEnableProbability   = 0.1
   mutateGeneReenableProbability   = 0.05
   mutateAddNeuronProbability      = 0.01
   mutateAddSynapseProbability     = 0.3
   interspeciesMateRate            = 0.001 # Prob. of a mate being outside species
   mateMultipointProbability       = 0.6
   mateMultipointAveProbability    = 0.4
   mateSinglepointProbability      = 0.0
   mateOnlyProbability             = 0.2 # Prob. of mating without mutation

   # Probability of forcing selection of ONLY links that are naturally recurrent
   recurrentProbability = 0.2

   populationSize   = 1000 # Size of population
   dropoffAge       =   15 # Age where Species starts to be penalized
   synapseAddTries  =   20 # Number of tries mutate_add_link will attempt to find an open link
   print_every      =    0 # Tells to print population to file every n generations

   babiesStolen     =    0 # The number of babies to siphen off to the champions

   numRuns          =    1 # The number of runs to average over in an experiment
   numGenerations   =  100

   numSpeciesTarget =  100

   sigmoidSlope     = 4.924273
   sigmoidConstant  = 2.4621365

def printConfiguration():
   members = inspect.getmembers(Configuration)
   for member in members:
      if not member[0].startswith('__'):
         print member[0], '=', member[1]

def loadConfiguration(fileName):
   fields = []
   members = inspect.getmembers(Configuration)
   for member in members:
      if not member[0].startswith('__'):
         fields.append(member[0])

   file = open(fileName)
   for line in file:
      line = line.strip().replace(' ', '')
      if not line.startswith('#'):
         key, value = line.split('=')
         if key in fields:
            type = 'int('
            if value.find('.') >= 0:
               type = 'float('
            exec('Configuration.' + key + ' = ' + type + 'value)')

   file.close()
