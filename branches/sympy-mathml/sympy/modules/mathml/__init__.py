"""Module with some functions for MathML, like transforming MathML
content in MathML presentation. 

To use this module, you will need libxml2 and libxslt, with it's
respective python bindings.
"""

import libxml2
import libxslt
from sympy.modules.pkgdata import get_resource


def mathml_ctop(mml, simple=False):
    """Transforms a document in MathML content (like the one that sympy preduces)
    in one document in MathML presentation, more suitable for printing, and more
    widely accepted
    """
    
    if simple:
        s = get_resource('mathml/data/simple_mmlctop.xsl').read()
    else:
        s = get_resource('mathml/data/mmlctop.xsl').read()

    styledoc = libxml2.parseDoc(s)
    style = libxslt.parseStylesheetDoc(styledoc)
    
    doc = libxml2.parseDoc(mml)
    result = style.applyStylesheet(doc, None)
    sourceDoc = result
    s = style.saveResultToString(result)
    
    style.freeStylesheet()
    sourceDoc.freeDoc()
    
    return s
    
    

