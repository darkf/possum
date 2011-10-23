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
      print "= %r" % evalString(text).value
    except Exception, e:
      traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
  main()