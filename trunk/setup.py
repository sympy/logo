#!/usr/bin/env python
"""Distutils based setup script for Sympy.

This uses Distutils (http://python.org/sigs/distutils-sig/) the standard
python mechanism for installing packages. For the easiest installation
just type the command (you'll probably need root privileges for that):

    python setup.py install

This will install the library in the default location. For instructions on
how to customize the install procedure read the output of:

    python setup.py --help install

In addition, there are some other commands:

    python setup.py bdist_dpkg -> will make a deb package in the parent diretory
    python setup.py clean -> will clean all trash (*.pyc and stuff)
    python setup.py test  -> will run the complete test suite
    python setup.py test_core -> will run only tests concerning core features
    python setup.py test_doc -> will run tests on the examples of the documentation
    
To get a full list of avaiable commands, read the output of: 

    python setup.py --help-commands
    
Or, if all else fails, feel free to write to the sympy list at
sympy@googlegroups.com and ask for help.
"""

from distutils.core import setup
from distutils.core import Command
import sys
import sympy

# Make sure I have the right Python version.
if sys.version_info[1] < 4:
    print "Sympy requires Python 2.4 or newer.  Python %d.%d detected" % \
          sys.version_info[:2]
    sys.exit(-1)

class test_sympy(Command):
    """Runs all tests under the tests/ folder
    """
    
    description = "Automatically run the test suite for Sympy."
    user_options = []  # distutils complains if this is not here.


    def initialize_options(self):  # distutils wants this
        pass
    
    def finalize_options(self):    # this too
        pass
    
    def run(self):
        try:
            import py
        except ImportError:
            print """In order to run the tests, you need codespeak's py.lib
            web page: http://codespeak.net/py/dist/
            If you are on debian systems, the package is named python-codespeak-lib
            """
            sys.exit(-1)
        py.test.cmdline.main(args=["tests"])
        test_sympy_doc.run_doctest() # run also the doc test suite
        
class bdist_dpkg(Command):
    """Make a nice .deb package
    """
    
    description = "Make a deb package using dpkg"
    user_options = []  # distutils complains if this is not here.
 
    __debversion__ = sympy.__version__ + "-2" # change this with a new 

    def initialize_options(self):  # distutils wants this
        pass
    
    def finalize_options(self):    # this too
        pass
    
    def run(self):
        import os
        revision=739
        os.system("svn -q export -r %d . sympy-svn%d" %(revision, revision))
        os.system("tar zcf sympy_%s~svn%d.orig.tar.gz sympy-svn%d" \
                %(sympy.__version__, revision, revision))
        os.system("cd sympy-svn%d; debuild -sa -us -uc" % revision)
        os.system("rm -rf sympy-svn%d" % (revision))
        #os.system("rm -rf /tmp/sympy-%s" % sympy.__version__)
        #os.system("svn export . /tmp/sympy-%s" % sympy.__version__)
        #print "-"*50
        #print "These files were created in /tmp:"
        #print "sympy_%s.orig.tar.gz" % sympy.__version__
        #print "sympy_%s_i386.changes" % self.__debversion__
        #print "sympy_%s.diff.gz" % self.__debversion__
        #print "sympy_%s.dsc" % self.__debversion__
        #print "python-sympy_%s_all.deb" % self.__debversion__

class clean(Command):
    """Cleans *.pyc and debian trashs, so you should get the same copy as 
    is in the svn.
    """
    
    description = "Clean everything"
    user_options = [("all","a","the same")]  

    def initialize_options(self):  
        self.all = None
    
    def finalize_options(self):   
        pass

    def run(self):
        import os
        os.system("py.cleanup")
        os.system("rm -f python-build-stamp-2.4")
        os.system("rm -f MANIFEST")
        os.system("rm -f debian/files")
        os.system("rm -f debian/python-sympy.substvars")
        os.system("rm -rf debian/python-sympy")
        os.system("rm -rf build")
        os.system("rm -rf dist")

class test_sympy_core(Command):
    """Run only the tests concerning features of sympy.core.
    It's a lot faster than running the complete test suite.
    """
    
    description = "Automatically run the core test suite for Sympy."
    user_options = []  # distutils complains if this is not here.

    tests_to_run = ["tests/test_arit.py", "tests/test_basic.py", 
                   "tests/test_diff.py", "tests/test_equal.py", 
                   "tests/test_eval.py", "tests/test_evalf.py", 
                   "tests/test_functions.py", "tests/test_hashing.py", 
                   "tests/test_numbers.py", "tests/test_series.py", 
                   "tests/test_str.py", "tests/test_subs.py", 
                   "tests/test_symbol.py"
                   ]
    
    def initialize_options(self):  # distutils wants this
        pass
    
    def finalize_options(self):    # this too
        pass

        
    def run(self):
        try:
            import py
        except ImportError:
            print """In order to run the tests, you need codespeak's py.lib
            web page: http://codespeak.net/py/dist/
            If you are on debian systems, the package is named python-codespeak-lib
            """
            sys.exit(-1)
        py.test.cmdline.main(args=self.tests_to_run)
        
class test_sympy_doc(Command):
    
    description = "Run the tests for the examples in the documentation"
    user_options = []  # distutils complains if this is not here.
    
    def initialize_options(self):  # distutils wants this
        pass
    
    def finalize_options(self):    # this too
        pass
    
    @staticmethod
    def run_doctest():
        
        import unittest
        import doctest
        
        import glob

        files = glob.glob('sympy/*/*.py') + glob.glob('sympy/modules/*/*.py')
        
        # files without doctests or that don't work
        files.remove('sympy/modules/printing/pygame_.py')
        files.remove('sympy/modules/printing/pretty.py') # see issue 53
        
        #testing for optional libraries
        try:
            import libxslt
        except ImportError:
            #remove tests that make use of libxslt1
            files.remove('sympy/modules/printing/latex.py')
            files.remove('sympy/modules/printing/__init__.py')

        modules = []
        for x in files:
            if len(x) > 12 and x[-11:] == '__init__.py':
                x = x.replace('/__init__', '') 
                print x
            modules.append(x.replace('/', '.')[:-3])
            #put . as separator and strip the extension (.py)

        modules.append('sympy')
        
        suite = unittest.TestSuite()
        for mod in modules:
            suite.addTest(doctest.DocTestSuite(mod))
            
        runner = unittest.TextTestRunner()
        runner.run(suite)

    def run(self):
        self.run_doctest()
        
import sympy

setup(
      name = 'sympy', 
      version = sympy.__version__, 
      description = 'Computer algebra system (CAS) in Python', 
      url = 'http://code.google.com/p/sympy', 
      packages = ['sympy', 'sympy.core', 'sympy.modules',
                  'sympy.modules.mathml', 'sympy.modules.printing'],
      package_data = {'sympy.modules.mathml' : ['data/mmlctop.xsl', 
                                                'data/mmltex.xsl',
                                                'data/simple_mmlctop.xsl' ]},
      scripts = ['bin/isympy'],
      ext_modules = [],
      data_files = [('share/man/man1', ['doc/man/isympy.1'])],
      cmdclass    = {'test': test_sympy, 
                     'test_core' : test_sympy_core,
                     'test_doc' : test_sympy_doc,
                     'bdist_dpkg' : bdist_dpkg, 
                     'clean' : clean, 
                     },
      )

