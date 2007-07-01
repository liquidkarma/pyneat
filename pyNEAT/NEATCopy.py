import copy
import cPickle

# cPickle appears to be much faster in my experiments than copy.deepcopy
# object copying centralized here for easy changes

def objectCopy(obj):
   if obj is None:
      return obj
   else:
      #return copy.deepcopy(obj)
      return cPickle.loads(cPickle.dumps(obj))
