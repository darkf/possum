import sys
from possum import evalFile, unbox

def main():
  if len(sys.argv) < 2:
    print "usage: %s FILE...[FILE2]" % sys.argv[0]
    return
    
  files = sys.argv[1:]
  
  for file in files:
    r = unbox(evalFile(file))
      
if __name__ == '__main__': main()