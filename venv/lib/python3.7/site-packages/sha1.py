#!/usr/bin/env python
"""
usage: python -m sha1 <filename>
       python -m sha1 < filename
"""
import sys
import hashlib

# --- these fields are required for packaging
__version__ = '1.2'
__author__ = 'anatoly techtonik <techtonik@gmail.com>'
__license__ = 'Public Domain'
__url__ = 'https://github.com/techtonik/sha1'
# /-- these fields are required for packaging

PY3K = sys.version_info >= (3, 0)

if sys.stdin.isatty():  # stdin is not piped
  if not sys.argv[1:]:
    sys.exit(__doc__.strip())
  source = open(sys.argv[1], 'rb')
else:
  if PY3K:
    source = sys.stdin.buffer
  else:
    # Python 2 on Windows opens sys.stdin in text mode, and
    # binary data that read from it becomes corrupted on \r\n
    if sys.platform == "win32":
      # set sys.stdin to binary mode
      import os, msvcrt
      msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    source = sys.stdin

sha1sum = hashlib.sha1()
block = source.read(2**16)
while len(block) != 0:
  sha1sum.update(block)
  block = source.read(2**16)
print(sha1sum.hexdigest())
source.close()

# quick test should give you this
#
#   $ sha1.py UNLICENSE 
#   fad0fbaf831fead007f4465821459c58a2973eb0
#   $ sha1.py < UNLICENSE 
#   fad0fbaf831fead007f4465821459c58a2973eb0
#   $ sha1.py < UNLICENSE.crlf
#   fbf569f14e87fd3191246450c5b519649e67a52c
