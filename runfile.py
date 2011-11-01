import sys
from possum import evalString

def main():
  if len(sys.argv) < 2:
    print "usage: %s FILE...[FILE2]" % sys.argv[0]
    return
    
  files = sys.argv[1:]
  
  for file in files:
    f = open(file, "r")
    try:
      evalString(f.read())
    except:
      raise
    finally:
      f.close()
      
if __name__ == '__main__': main()