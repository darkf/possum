# possum lang - v0.01
# copyright (c) 2011 darkf
# released under the MIT license
#
# the REPL component of possum

from possum import evalString

def main():
  while True:
    text = raw_input("> ")
    
    if text in [":q", ":quit", ":exit"]:
      print "<bye>"
      break
    
    try:
      evalString(text)
    except Exception, e:
      print "<error> %r" % e

if __name__ == '__main__':
  main()