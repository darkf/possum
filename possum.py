# possum lang - v0.02
# copyright (c) 2011 darkf
# released under the MIT license
#
# meant to be a semi-esoteric language
# it's basically just a small subset of a pseudo-lisp
# with fixed-arity functions and implicit grouping
#
# e.g.
# print minus plus plus 1 5 3 1
# is like
# (print (minus (plus (plus 1 5) 3) 1))
#
# here's a more sophisticated example (ported from scheme)
#
#  defun list-sum 1 x
#    cond 3
#      or nil? x empty? x
#        0
#      pair? car x
#        plus list-sum car x list-sum cdr x
#      true
#        plus car x list-sum cdr x
#        
#  set "lst" cons 1 cons 2 cons 3 nil
#  print list-sum lst
#
#
# TODO:
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

class Node:
  def __init__(self, value):
    self.value = value

class StringNode(Node): pass
class IntNode(Node):    pass
class BoolNode(Node):   pass
class ListNode(Node):   pass

class NilNode(Node):
  def __init__(self): self.value = None

class AtomNode(Node):
  def __repr__(self): return "<atom %r>" % self.value
    
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
  if isinstance(x, Node):
    return x.value
  if isinstance(x, Function):
    return x
  
  raise Exception("<InternalError> fixme: shouldn't be here either? (unbox %r)" % x)
  
def box(x):
  if type(x) == int:  return IntNode(x)
  if type(x) == str:  return StringNode(x)
  if type(x) == bool: return BoolNode(x)
  if type(x) == list: return ListNode(x)
  if x is None:       return NilNode()
  
  if isinstance(x, Node):     return x
  if isinstance(x, Function): return x
  
  raise Exception("<InternalError> fixme: don't know what to box (%r)" % x)
  
def _print(x): print ":", x
def _plus(x, y): return x + y
def _minus(x, y): return x - y
def _mul(x, y): return x * y
def _div(x, y): return x / y
def _mod(x, y): return x % y
def _pow(x, y): return x ** y
def _cons(x, y): return [x, y] # creates a pair
def _car(x): return x[0]
def _cdr(x): return x[1]
def _set(x, y):
  global sym_global, callstack
  if len(callstack) > 1:
    callstack[-2].env.set(x, box(y))
  else:
    sym_global.set(x, box(y))
def _setglobal(x, y):
  global sym_global
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
def _eqp(x, y): return x == y
def _nilp(x): return x is None
def _not(x): return not x
def _or(x, y): return x or y
def _and(x, y): return x and y
def _defp(x): return lookup(x) is not None
def _pairp(x): return type(x) == list and len(x) == 2
def _emptyp(x): return type(x) != list or len(x) == 0

def _lt(x, y): return x < y
def _gt(x, y): return x > y
def _lteq(x, y): return x <= y
def _gteq(x, y): return x >= y

class Environment:
  def __init__(self, sym=None, prev=None):
    if sym is None:
      sym = {}
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
  def __init__(self, fun, args, locals=None):
    global sym_global
    self.fun = fun
    self.args = args
    if locals is None:
      locals = {}
    self.env = Environment(locals, prev=sym_global)

sym_global = Environment({"print": Function("print", 1, _print),
       "plus": Function("plus", 2, _plus),
       "minus": Function("minus", 2, _minus),
       "mul": Function("mul", 2, _mul),
       "div": Function("div", 2, _div),
       "mod": Function("mod", 2, _mod),
       "pow": Function("pow", 2, _pow),
       "eq?": Function("eq?", 2, _eqp),
       "nil?": Function("nil?", 1, _nilp),
       "not": Function("not", 1, _not),
       "or": Function("or", 2, _or),
       "and": Function("and", 2, _and),
       "def?": Function("def?", 1, _defp),
       "pair?": Function("pair?", 1, _pairp),
       "empty?": Function("empty?", 1, _emptyp),
       "<": Function("<", 2, _lt),
       ">": Function(">", 2, _gt),
       "<=": Function("<=", 2, _lteq),
       ">=": Function(">=", 2, _gteq),
       "cons": Function("cons", 2, _cons),
       "car": Function("car", 1, _car),
       "cdr": Function("cdr", 1, _cdr),
       "set": Function("set", 2, _set),
       "setglobal": Function("setglobal", 2, _setglobal),
       "printsym": Function("printsym", 0, _printsym)})
       
callstack = []

def lookup(sym):
  return peekCallEnv().lookup(sym)
  
def set(sym, val):
  return peekCallEnv().set(sym, val)
  
def setglobal(sym, val):
  return sym_global.set(sym, val)
  
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

  # create closure to execute function
  def _fn(*fnargs):
    for i,arg in enumerate(args):
      set(arg.value, box(fnargs[i]))
    return unbox(evalTokens(Consumer(body)))
  
  return Function("<lambda>", n.value, _fn)
  
def do_defun(tc):
  # defun special form
  # form: defun add 2 x y plus x y
  # is like (defun add (x y) (+ x y))
  
  name = tc.consume() # we avoid it being treated as a function application
  n = evalArg(tc)
  
  if not isinstance(n, IntNode):
    raise Exception("<TypeError> second argument to defun must be an integer")
    
  args = consumeArgs(tc, n.value)
  
  # forward-declare function so that named recursion works
  fn = setglobal(name.value, Function(name.value, n.value, None))
  
  body = consumeArgs(tc, 1)
  
  # create closure to execute function
  def _fn(*fnargs):
    for i,arg in enumerate(args):
      set(arg.value, box(fnargs[i]))
    return unbox(evalTokens(Consumer(body)))
    
  fn.fn = _fn
  return box(None)
  
def do_case(tc):
  # case special-form
  # form: case 2 value "value one" "you chose value 1" else "you didn't choose 1 or 2"
  # hint: it's like a switch statement
  
  n = evalArg(tc)
  if not isinstance(n, IntNode):
    raise Exception("<TypeError> first argument to case must be an integer")
    
  val = evalArg(tc)
  for i in range(n.value):
    if isinstance(tc.peek(), AtomNode) and tc.peek().value == "else":
      tc.consume()
      return evalArg(tc)
      
    t = evalArg(tc)
    if t.value == val.value:
      r = evalArg(tc)
      # consume everything that wasn't matched after this
      consumeArgs(tc, (n.value-i)*2)
      return r
    else:
      tc.consume() # do nothing with it
      
  return box(None)
  
def do_cond(tc):
  # cond special-form
  # form: cond 2 nil? x "x = nil" else "x is not nil"
  
  n = evalArg(tc)
  if not isinstance(n, IntNode):
    raise Exception("<TypeError> first argument to cond must be an integer")
    
  for i in range(n.value):
    if isinstance(tc.peek(), AtomNode) and tc.peek().value == "else":
      tc.consume()
      return evalArg(tc)
      
    t = evalArg(tc)
    if t.value: # truthfulness
      r = evalArg(tc)
      consumeArgs(tc, (n.value-i)*2)
      return r
    else:
      tc.consume()
      
  return box(None)
    
def evalArg(tc):
  t = tc.consume()
  
  if isinstance(t, AtomNode):
    # evaluate special-forms
    if t.value == "lambda": return do_lambda(tc)
    if t.value == "case":   return do_case(tc)
    if t.value == "cond":   return do_cond(tc)
    if t.value == "defun":  return do_defun(tc)
      
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
    r = evalArg(tc)
  return r
    
def evalArgs(tc, arity):
  out = []
  for i in range(arity):
    out.append(evalArg(tc))
  return out

def consumeArg(tc, recurse_arity=-1):
  t = tc.consume()
  if isinstance(t, AtomNode):
    if t.value == "cond":
      x = [t]
      n = tc.consume()
      x.append(n)
      x.extend(consumeArgs(tc, n.value*2))
      return x
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