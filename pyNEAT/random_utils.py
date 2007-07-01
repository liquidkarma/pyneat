import random

random.seed()

def randfloat():
   return random.random()

def randbit():
   return random.randint(0, 1)

def randposneg():
   if randbit() == 1:
      return 1
   else:
      return 0
