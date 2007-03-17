"""Printing using GtkMathView"""

from sympy.core import Basic
from sympy.modules.mathml import mathml_ctop
import tempfile
import os

def print_gtk(x):
    """Print to Gtkmathview, a gtk widget capable of rendering MathML.
    Needs libgtkmathview-bin"""
    
    assert isinstance(x, Basic)
    
    tmp = tempfile.mktemp() # create a temp file to store the result
    file = open(tmp, 'wb')
    
    file.write( mathml_ctop(x.mathml()) )
    file.close()
    
    os.system("mathmlviewer " + tmp)
    
    file = open(tmp)
    
    print file.read()
    
