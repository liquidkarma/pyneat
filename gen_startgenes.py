#!/usr/bin/python

import sys

if __name__ == '__main__':
   if len(sys.argv) != 4:
      print 'usage:', sys.argv[0], 'NUM_INPUTS NUM_HIDDEN NUM_OUTPUTS'
      print '   creates start genes file, dumping output to the screen'
      print '   output can then be redirected to an appropriate file'
   else:
      numInputs  = int(sys.argv[1])
      numHidden  = int(sys.argv[2])
      numOutputs = int(sys.argv[3])

      numConnections = (numInputs + 1) * numHidden + numHidden * numOutputs

      print 'genomestart 1'

      for i in range(1, numConnections + 1):
         print 'trait', i, '0 0 0 0 0 0 0 0'

      print 'node 1 0 1 3'

      for i in range(2, 2 + numInputs):
         print 'node', i, '0 1 1'

      for i in range(2 + numInputs, 2 + numInputs + numHidden):
         print 'node', i, '0 1 0'

      for i in range(2 + numInputs + numHidden, 2 + numInputs + numHidden + numOutputs):
         print 'node', i, '0 0 2'

      gene = 1
      for i in range(1, 2 + numInputs):
         for j in range(2 + numInputs, 2 + numInputs + numHidden):
            print 'gene', gene, i, j, '0.5 0', gene, '0 1'
            gene += 1

      for i in range(2 + numInputs, 2 + numInputs + numHidden):
         for j in range(2 + numInputs + numHidden, 2 + numInputs + numHidden + numOutputs):
            print 'gene', gene, i, j, '0.5 0', gene, '0 1'
            gene += 1

      print 'genomeend 1'
