# Dumb Language - v0.01
# (c) 2011 darkf
# released under the MIT license
#
# meant to be a semi-esoteric language
# it's basically just a lisp with fixed-arity functions and implicit grouping
#
# e.g.
# print minus plus plus 1 5 3 1
# is like
# (print (minus (plus (plus 1 5) 3) 1))
#
# TODO:
# - add nil type
# - add function definition
# - make python function definitions infer arity
# - actually parse strings
# - make parser work with multiple toplevel statements
# - add typechecking and signatures
# - diagnostics
# - stdlib
# - unit tests
# - clean up code (heh, yeah right)
# - document code (hah, hah-hah...)

TEST_STRING = 'print minus plus plus 1 5 3 1'

class StringNode:
  def __init__(self, value):
    self.value = value
    
class IntNode:
  def __init__(self, value):
    self.value = value
    
class AtomNode:
  def __init__(self, value):
    self.value = value
    
class CallNode:
  def __init__(self, atom, args):
    self.atom = atom
    self.args = args
    self.arity = len(args)
    
class Function:
  def __init__(self, atom, arity, fn):
    self.atom = atom
    self.arity = arity
    self.fn = fn

def parse(text):
  s = text.split()
  out = []
  for t in s:
    if t[0] == '"':
      out.append(StringNode(t[1:-1]))
    else:
      try:
        out.append(IntNode(int(t)))
      except ValueError:
        out.append(AtomNode(t))
  return out
  
def unbox(x):
  if isinstance(x, IntNode):
    return x.value
  if isinstance(x, StringNode):
    return x.value
  if isinstance(x, AtomNode):
    print "fixme: shouldn't be here?"
    return x.value
    
  print "fixme: shouldn't be here either?"
  
def box(x):
  if type(x) == int:
    return IntNode(x)
  if type(x) == str:
    return StringNode(x)
  print "fixme: don't know what to box (%r)" % x
  return None
  
def _print(x):
  'string->int'
  print ":", x
  return 1337
def _plus(x,y):
  'int,int->int'
  return x+y
def _minus(x,y):
  return x-y

sym = {"print": Function("print", 1, _print),
       "plus": Function("+", 2, _plus),
       "minus": Function("-", 2, _minus)}
       
class Consumer:
  def __init__(self, toks):
    self.toks = toks
    self.index = 0
    
  def peek(self, n=0):
    if self.index+n >= len(self.toks):
      return None
    return self.toks[self.index+n]
    
  def consume(self):
    if self.index >= len(self.toks):
      return None
    r = self.toks[self.index]
    self.index += 1
    return r
    
def lookup(x):
  return sym.get(x, None)
    
def do_fcall(tc, atom):
  fn = lookup(atom)
  if fn is None:
    print "no function '%s'" % atom
    raise Exception()
    
  #sig = fn.fn.__doc__
  #t_in, t_out = sig.split("->")
  #t_in = t_in.split(",")
    
  args = evalArgs(tc, fn.arity)
  
  #for arg in args:
  #  if 
  
  # unbox args
  args_unboxed = map(unbox, args)
  
  return box( fn.fn(*args_unboxed) )
    
def evalArg(tc):
  t = tc.consume()
  
  if isinstance(t, AtomNode):
    # assume fcall
    return do_fcall(tc, t.value)
    
  if isinstance(t, IntNode):
    return t
    
  if isinstance(t, StringNode):
    return t
    
def evalArgs(tc, arity):
  out = []
  for i in range(arity):
    out.append(evalArg(tc))
  return out
  
def eval(tc):
  out = []
  i = 0
  
  while True:
    t = tc.peek()
    if isinstance(t, AtomNode):
      # assume fcall
      tc.consume()
      do_fcall(tc, t.value)
    if t is None:
      break
        
def main():
  tc = Consumer(parse(TEST_STRING))
  eval(tc)
        
if __name__ == '__main__':
  main()