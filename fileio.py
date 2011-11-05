# file i/o module for possum
# copyright (c) 2011 darkf
# under the MIT license
#
# file-open filename mode
# file-read fd bytes
# file-write fd str
# file-close fd

from possum import setglobal, Function

fds = {}

def _file_open(filename, mode):
  global fds
  f = open(filename, mode)
  fd = f.fileno()
  fds[fd] = f
  return fd
  
def _file_read(fd, bytes):
  return fds[fd].read(bytes)
  
def _file_readall(fd):
  return fds[fd].read()
  
def _file_write(fd, str):
  return fds[fd].write(str)
  
def _file_close(fd):
  fds[fd].close()
  del fds[fd]
  
setglobal("file-open", Function("file-open", 2, _file_open))
setglobal("file-read", Function("file-read", 2, _file_read))
setglobal("file-readall", Function("file-readall", 1, _file_readall))
setglobal("file-write", Function("file-write", 2, _file_write))
setglobal("file-close", Function("file-close", 1, _file_close))
