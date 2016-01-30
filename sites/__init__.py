"""
Module containing defintions for all sites to test. Should be subclasses
of 'browser_base'.
"""

import os
import imp

sites = {}


for fle in os.listdir(__path__[0]):
      name, ext = os.path.splitext(fle)
      if ext == '.py' and not name == "__init__":
            sites[name] = imp.load_source(name, os.path.join(__path__[0], fle))
