#!/usr/bin/env python

# Copyright (c) 2009 Google Inc. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import sys

# Make sure we're using the version of pylib in this repo, not one installed
# elsewhere on the system.
#sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'pylib'))
#
# CUSTOM: Above line commented out and replaced with below, because of this error:
#         ImportError: No module named gyp
#         Issue link: https://github.com/nodejs/node-gyp/issues/1782
#         for some reason `sys.argv[0]` gives back empty string
#
gypPath = os.path.join(sys.path[0], 'pylib')
sys.path.insert(0, gypPath)
print "CUSTOM: The path that will be used to load 'gyp' module is " + gypPath

import gyp


if __name__ == '__main__':
  sys.exit(gyp.script_main())
