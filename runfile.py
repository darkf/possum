import sys
from possum import evalFile, unbox
import fileio

def main():
  if len(sys.argv) < 2:
    print "usage: %s FILE...[FILE2]" % sys.argv[0]
    return
    
  map(evalFile, sys.argv[1:])
      
if __name__ == '__main__': main()