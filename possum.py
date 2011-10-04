# possum lang - v0.01
# copyright (c) 2011 darkf
# released under the MIT license
#
# meant to be a semi-esoteric language
# it's basically just a small subset of lisp
# with fixed-arity functions and implicit grouping
#
# e.g.
# print minus plus plus 1 5 3 1
# is like
# (print (minus (plus (plus 1 5) 3) 1))
#
# TODO:
# - add function definition
# - make python function definitions infer arity
# - actually parse strings
# - make parser work with multiple toplevel statements
# - add typechecking and signatures
# - diagnostics
# - stdlib
# - at least somewhat verify correctness
# - modules (or at least including)
# - unit tests
# - clean up code (heh, yeah right)
# - document code (hah, hah-hah...)
#
# Open questions:
# - should operators use symbols or names? (e.g. + - / or plus minus div)
# - should we have an atom quote operator?
#   (e.g. 'x which returns an atom rather than the value of x)
#   so we could do stuff like set 'x 5 rather than set "x" 5

#TEST_STRING = 'print minus plus plus 1 5 3 1'
#TEST_STRING = 'print if true "yes" "no"'
#TEST_STRING = 'print car cdr cdr cons 1 cons 2 cons 3 cons 4 cons 5 nil'
TEST_STRING = 'print set "x" 5'

class StringNode:
  def __init__(self, value):
    self.value = value
    
class IntNode:
  def __init__(self, value):
    self.value = value
    
class BoolNode:
  def __init__(self, value):
    self.value = value
    
class ListNode:
  def __init__(self, value):
    self.value = value
    
class NilNode:
  def __init__(self):
    self.value = None
    
class AtomNode:
  def __init__(self, value):
    self.value = value
    
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
        if isbool(t):
          out.append(BoolNode(parsebool(t)))
        elif t.lower() == "nil":
          out.append(NilNode())
        else:
          out.append(AtomNode(t))
  return out
  
def parsebool(x):
  return x.lower() == "true"
  
def isbool(x):
  return x.lower() == "true" or x.lower() == "false"
  
def unbox(x):
  if isinstance(x, IntNode):
    return x.value
  if isinstance(x, StringNode):
    return x.value
  if isinstance(x, AtomNode):
    print "fixme: shouldn't be here?"
    return x.value
  if isinstance(x, BoolNode):
    return x.value
  if isinstance(x, ListNode):
    return x.value
  if isinstance(x, NilNode):
    return x.value
  
  print "fixme: shouldn't be here either? (unbox %r)" % x
  
def box(x):
  # XXX: if it's already boxed, we'll fall through
  if type(x) == int:
    return IntNode(x)
  if type(x) == str:
    return StringNode(x)
  if type(x) == bool:
    return BoolNode(x)
  if type(x) == list:
    return ListNode(x)
  if x is None:
    return NilNode()
  print "fixme: don't know what to box (%r)" % x
  return None
  
def _print(x):
  'string->int'
  print ":", x
def _plus(x, y):
  'int,int->int'
  return x + y
def _minus(x, y):
  return x - y
def _if(c, t, e):
  if c == True:
    return t
  return e
def _cons(x, y):
  return [x] + [y]
def _car(x):
  return x[0]
def _cdr(x):
  return x[1]
def _set(x, y):
  sym[x] = box(y)
  return y

sym = {"print": Function("print", 1, _print),
       "plus": Function("+", 2, _plus),
       "minus": Function("-", 2, _minus),
       "if": Function("if", 3, _if),
       "cons": Function("cons", 2, _cons),
       "car": Function("car", 1, _car),
       "cdr": Function("cdr", 1, _cdr),
       "set": Function("set", 2, _set)}
       
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
    elif t is None:
      break
    else:
      print "top-level token that isn't an atom, panic (%r)" % t
        
def main():
  tc = Consumer(parse(TEST_STRING))
  eval(tc)
        
if __name__ == '__main__':
  main()