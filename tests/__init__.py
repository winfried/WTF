"""
Module containing defintions for all tests to perform.
"""

import os
import imp

tests = {}


for fle in os.listdir(__path__[0]):
      name, ext = os.path.splitext(fle)
      if ext == '.py' and not name == "__init__":
            tests[name] = imp.load_source(name, os.path.join(__path__[0], fle))
