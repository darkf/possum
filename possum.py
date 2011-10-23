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

# XXX: should be one top-level Node class
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
    raise Exception("<unbox> shouldn't be here (was passed an atom)")
  if isinstance(x, BoolNode):
    return x.value
  if isinstance(x, ListNode):
    return x.value
  if isinstance(x, NilNode):
    return x.value
  if isinstance(x, Function):
    return x
  
  raise Exception("<InternalError> fixme: shouldn't be here either? (unbox %r)" % x)
  
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
  if isinstance(x, Function):
    return x
  if x is None:
    return NilNode()
  raise Exception("<InternalError> fixme: don't know what to box (%r)" % x)
  
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
  global sym_global, callstack
  if len(callstack) > 1:
    callstack[-2].env.set(x, box(y))
  else:
    sym_global.set(x, box(y))
def _printsym(d=0, sym=None):
  if d == 0:
    print "symbols:"
    
  if sym is None:
    sym = peekCallEnv()
    
  print "[%d]" % d
  for k,v in sym.sym.iteritems():
    print "%s: %r" % (k, v)
  
  if sym.prev is not None:
    _printsym(d+1, sym.prev)
  
class Environment:
  def __init__(self, sym={}, prev=None):
    self.sym = sym
    self.prev = prev
    
  def lookup(self, sym):
    if self.sym.has_key(sym):
      return self.sym[sym]
    
    # recursively look up to parent scopes
    if self.prev is not None:
      return self.prev.lookup(sym)
    
    # we're at the top of the scope and it hasn't been found, let's just fail
    return None
    
  def set(self, sym, val):
    self.sym[sym] = val
    return val
    
class Call:
  def __init__(self, fun, args, locals={}):
    global sym_global
    self.fun = fun
    self.args = args
    self.env = Environment(locals, prev=sym_global)

sym_global = Environment({"print": Function("print", 1, _print),
       "plus": Function("+", 2, _plus),
       "minus": Function("-", 2, _minus),
       "if": Function("if", 3, _if),
       "cons": Function("cons", 2, _cons),
       "car": Function("car", 1, _car),
       "cdr": Function("cdr", 1, _cdr),
       "set": Function("set", 2, _set),
       "printsym": Function("printsym", 0, _printsym)})
       
callstack = []

def lookup(sym):
  return peekCallEnv().lookup(sym)
  
def set(sym, val):
  return peekCallEnv().set(sym, val)
  
def pushCall(call):
  global callstack
  callstack.append(call)
  
def popCallEnv():
  global callstack
  return callstack.pop().env
  
def peekCallEnv():
  global callstack, sym_global
  if len(callstack) >  0:
    return callstack[-1].env
  return sym_global
       
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
    
def do_call_func(tc, fn):
  # XXX: typechecking stuff if necessary
  #sig = fn.fn.__doc__
  #t_in, t_out = sig.split("->")
  #t_in = t_in.split(",")
  #print "calling %s with %d args" % (fn.atom, fn.arity)
  args = evalArgs(tc, fn.arity)
  
  # unbox args
  args_unboxed = map(unbox, args)
  
  pushCall(Call(fn, args))
  r = box( fn.fn(*args_unboxed) )
  popCallEnv()
  return r
  
def do_lambda(tc):
  # hit a lambda special-form
  # form: lambda 2 x y * x y
  # which is the same as the s-expr (lambda (x y) (* x y))
  # (2 is the number of arguments to consume)
  
  n = evalArg(tc)
  if not isinstance(n, IntNode):
    raise Exception("<TypeError> first argument to lambda must be an integer")
  
  args = consumeArgs(tc, n.value)
  body = consumeArgs(tc, 1)
  
  print "def body:", body

  # create closure to execute function
  def _fn(*fnargs):
    for i,arg in enumerate(args):
      set(arg.value, fnargs[i])
    print "_fn:", list(fnargs)
    print "body:", body
    return unbox(evalTokens(Consumer(body)))
  
  fn = Function("<lambda>", n.value, _fn)
  return fn
    
def evalToken(tc):
  t = tc.consume()
  
  if isinstance(t, AtomNode):
    if t.value == "lambda":
      return do_lambda(tc)
    # we look up the atom in the symbol table,
    # and if it's a function, call it, otherwise return its value.
    val = lookup(t.value)
    if val is None:
      raise Exception("<BindingError> no such binding '%s'" % t.value)
    
    if isinstance(val, Function):
      # function -- call it
      return do_call_func(tc, val)
    # otherwise it's a variable, return its value
    return val
  
  return t
  
def evalTokens(tc):
  r = None
  while True:
    t = tc.peek()
    if t is None:
      break
    r = evalToken(tc)
  return r
    
def evalArg(tc):
  return evalToken(tc)
    
def evalArgs(tc, arity):
  out = []
  for i in range(arity):
    out.append(evalArg(tc))
  return out

def consumeArg(tc):
  t = tc.consume()
  if isinstance(t, AtomNode):
    val = lookup(t.value)
    if val is None:
      # not a known function, so assume it's not one and return the atom
      return t
    
    if isinstance(val, Function):
      return [t] + consumeArgs(tc, val.arity)
    # otherwise it's a variable, return its value
    return val
    
  return t
  
def consumeArgs(tc, arity):
  out = []
  for i in range(arity):
    t = consumeArg(tc)
    if type(t) == list:
      out.extend(t)
    else:
      out.append(t)
  return out
  
def evalConsumer(tc):
  r = None
  
  while True:
    t = tc.peek()
    if t is None:
      break
    r = evalArg(tc)
  return r
  
def evalString(text):
  return evalConsumer(Consumer(parse(text)))