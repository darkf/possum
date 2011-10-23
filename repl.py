# possum lang - v0.01
# copyright (c) 2011 darkf
# released under the MIT license
#
# the REPL component of possum

import sys, traceback
from possum import evalString

def main():
  while True:
    text = raw_input("> ")
    
    if text in [":q", ":quit", ":exit"]:
      print "<bye>"
      break
    
    try:
      # XXX: need a way to pretty-print values
      #x = "# %r" % evalString(text)
      #print x
      evalString(text)
    except Exception, e:
      print "<error> %r" % e
      traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
  main()