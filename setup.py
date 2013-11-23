#!/usr/bin/env python

# Copyright 2013 Ryan Volz

# This file is part of radarmodel.

# Radarmodel is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Radarmodel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with radarmodel.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import copy
from distutils.core import setup, Extension, Command
import numpy as np

try:
    from Cython.Compiler.Main import compile, CompilationResultSet
    from Cython.Compiler.Options import parse_directive_list
except ImportError:
    cython = False
else:
    cython = True

ext_modules = []

cython_modules = [Extension('radarmodel.libpoint_forward',
                            sources=['radarmodel/libpoint_forward.c'],
                            include_dirs=[np.get_include(), 'radarmodel/include'],
                            extra_compile_args=['-O3', '-ffast-math', '-fopenmp'],
                            extra_link_args=['-O3', '-ffast-math', '-fopenmp']),
                  Extension('radarmodel.libpoint_adjoint',
                            sources=['radarmodel/libpoint_adjoint.c'],
                            include_dirs=[np.get_include(), 'radarmodel/include'],
                            extra_compile_args=['-O3', '-ffast-math', '-fopenmp'],
                            extra_link_args=['-O3', '-ffast-math', '-fopenmp']),
                  Extension('radarmodel.libpoint_forward_alt',
                            sources=['radarmodel/libpoint_forward_alt.c'],
                            include_dirs=[np.get_include(), 'radarmodel/include'],
                            extra_compile_args=['-O3', '-ffast-math', '-fopenmp'],
                            extra_link_args=['-O3', '-ffast-math', '-fopenmp']),
                  Extension('radarmodel.libpoint_adjoint_alt',
                            sources=['radarmodel/libpoint_adjoint_alt.c'],
                            include_dirs=[np.get_include(), 'radarmodel/include'],
                            extra_compile_args=['-O3', '-ffast-math', '-fopenmp'],
                            extra_link_args=['-O3', '-ffast-math', '-fopenmp'])]
# add C-files from cython modules to extension modules
ext_modules.extend(cython_modules)

cython_extensions = []
for c_mod in cython_modules:
    cython_ext = copy.copy(c_mod)
    cython_ext.sources = [root + '.pyx' for root, ext 
                          in map(os.path.splitext, c_mod.sources) 
                          if ext.lower() == '.c']
    
    cython_extensions.append(cython_ext)

cmdclass = dict()

if cython:
    class CythonCommand(Command):
        """Distutils command to cythonize source files."""
        
        description = "compile Cython code to C code"
        
        user_options = [('annotate', 'a', 'Produce a colorized HTML version of the source.'),
                        ('directive=', 'X', 'Overrides a compiler directive.'),
                        ('timestamps', 't', 'Only compile newer source files.')]
        
        def initialize_options(self):
            self.annotate = False
            self.directive = ''
            self.timestamps = False
        
        def finalize_options(self):
            self.directive = parse_directive_list(self.directive)
        
        def run(self):
            results = CompilationResultSet()
            
            for cython_ext in cython_extensions:                
                res = compile(cython_ext.sources,
                              include_path=cython_ext.include_dirs,
                              verbose=True,
                              timestamps=self.timestamps,
                              annotate=self.annotate,
                              compiler_directives=self.directive)
                if res:
                    results.update(res)
                    results.num_errors += res.num_errors
            
            if results.num_errors > 0:
                sys.stderr.write('Cython compilation failed!')

    cmdclass['cython'] = CythonCommand

setup(name='radarmodel',
      version='0.1-dev',
      maintainer='Ryan Volz',
      maintainer_email='ryan.volz@gmail.com',
      url='http://sess.stanford.edu',
      description='Radar Modeling',
      long_description='',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Cython',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Topic :: Scientific/Engineering'],
      packages=['radarmodel'],
      package_data={'radarmodel': ['include/*']},
      cmdclass=cmdclass,
      ext_modules=ext_modules)