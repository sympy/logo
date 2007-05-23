
from basic import Basic, AssocOp

class Mul(AssocOp):

    @property
    def identity(self):
        return Basic.One()

            
