import math

def sumSquaredError(outputs, targets):
   if len(targets) != len(outputs):
      raise Exception('Invalid number of targets')

   error = 0.0

   for i in range(len(targets)):
      delta = outputs[i] - targets[i]
      error += delta * delta

   return math.sqrt(error)

def rootMeanSquaredError(outputs, targets):
   if len(targets) != len(outputs):
      raise Exception('Invalid number of targets')

   error = 0.0

   for i in range(len(targets)):
      delta = outputs[i] - targets[i]
      error += delta * delta

   return math.sqrt(error / len(targets))

def meanError(outputs, targets):
   if len(targets) != len(outputs):
      raise Exception('Invalid number of targets')

   error = 0.0

   for i in range(len(targets)):
      delta = outputs[i] - targets[i]
      error += delta * delta

   return error * 0.5
