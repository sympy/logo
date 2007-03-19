"""Module with some functions for MathML, like transforming MathML
content in MathML presentation. 

To use this module, you will need libxml2 and libxslt, with it's
respective python bindings.
"""

import libxml2
import libxslt
from sympy.modules.pkgdata import get_resource

def add_mathml_headers(s):
    return """<math xmlns:mml="http://www.w3.org/1998/Math/MathML"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.w3.org/1998/Math/MathML
        http://www.w3.org/Math/XMLSchema/mathml2/mathml2.xsd">\n  """ + s + "\n</math>"


def apply_xsl(mml, xsl):
    """Apply a xsl to a MathML string
    @param mml: a string with MathML code
    @param xsl: a string representing a path to a xsl (xml sylesheet) 
        file. This file name is relative to the PYTHONPATH
    """
    
    s = get_resource(xsl).read()
    
    styledoc = libxml2.parseDoc(s)
    style = libxslt.parseStylesheetDoc(styledoc)
    
    doc = libxml2.parseDoc(mml)
    result = style.applyStylesheet(doc, None)
    sourceDoc = result
    s = style.saveResultToString(result)
    
    style.freeStylesheet()
    sourceDoc.freeDoc()
    
    return s
    
def c2p(mml, simple=False):
    """Transforms a document in MathML content (like the one that sympy preduces)
    in one document in MathML presentation, more suitable for printing, and more
    widely accepted
    """
    
    if not mml.startswith('<math'):
        mml = add_mathml_headers(mml)
    
    if simple:
        return apply_xsl(mml, 'mathml/data/simple_mmlctop.xsl')
    
    return apply_xsl(mml, 'mathml/data/mmlctop.xsl')
    
def mml2latex(mml):
    """Translate ContetMathML (like the one that sympy produces) into 
    latex. 
    
    Example
    =======
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> from sympy.modules.mathml import mml2latex
        >>> print mml2latex( integrate(x*y+1, x, evaluate=False).mathml)
        $\int \left( 1 +yx\right)dx$

    """
    
    return apply_xsl(c2p(mml), 'mathml/data/mmltex.xsl')

