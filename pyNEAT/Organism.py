class Organism:
   def __init__(self, fitness, genome, generation):
      self.originalFitness         = fitness
      self.fitness                 = fitness
      self.genome                  = genome
      self.generation              = generation
      self.species                 = None
      self.expectedOffspring       = 0
      self.maxFitness              = 0.0
      self.eliminated              = False

      self.superChampionOffspring  = 0
      self.populationChampion      = False
      self.populationChampionChild = False

      self.speciesChampion         = False

      self.network                 = genome.genesis(genome.id)

   # descending order of fitness
   def __cmp__(self, other):
      return other.originalFitness - self.originalFitness

   def isCompatibleWith(self, organism):
      return self.genome.isCompatibleWith(organism.genome)
