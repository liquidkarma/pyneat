import math

# RIGHT SHIFTED
# ave 3213 clean on 40 runs of p2m and 3468 on another 40
# 41394 with 1 failure on 8 runs
#def sigmoid_right(x):
#   return (1.0 / (1.0 + math.exp(-(slope * x - constant))))

# LEFT SHIFTED
# original setting ave 3423 on 40 runs of p2m, 3729 and 1 failure also
#def sigmoid_left(x):
#   return (1.0 / (1.0 + math.exp(-(slope * x + constant))))

# LEFT SHIFTED NON-STEEPENED
# simple left shifted
#def sigmoid_leftnonsteepened():
#   return (1.0 / (1.0 + math.exp(-x - constant)))

# NON-SHIFTED STEEPENED
def sigmoid_nonshifted(x, slope):
   return (1.0 / (1.0 + math.exp(-(slope * x))))

def dsigmoid_nonshifted(x, slope):
   return (slope * x * (1.0 - x))

# TANH SIGMOID
def sigmoid_tanh(x):
   return math.tanh(x)

def dsigmoid_tanh(x):
   return (1.0 - x * x)

# PLAIN SIGMOID
def sigmoid(x):
   return (1.0 / (1.0 + math.exp(-x)))

def dsigmoid(x):
   return (x * (1.0 - x))

def activate(x, slope, constant):
   return sigmoid_nonshifted(x, slope)

def dactivate(x, slope, constant):
   return dsigmoid_nonshifted(x, slope)
