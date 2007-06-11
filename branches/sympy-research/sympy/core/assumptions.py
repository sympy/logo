
class AssumeMeths(object):
    """ Define default assumption methods.
    
    AssumeMeths should be used to derive Basic class only.

    All symbolic objects have assumption attributes that
    can be accessed via .is_<assumption name> attribute.
    Assumptions determine certain properties of symbolic
    objects. Assumptions can have 3 possible values: True, False, None.
    None is returned when is not possible to say something
    about the property. For example, ImaginaryUnit() is
    not positive neither negative.

    Here follows a list of possible assumption names:

        - commutative   - object commutes with any other object with
                          respect to multiplication operation.
        - real          - object can have only values from the set
                          of real numbers
        - integer       - object can have only values from the set
                          of integers
        - bounded       - object absolute value is bounded
        - dummy         - used for marking dummy symbols
        - positive      - object can have only positive values
        - nonnegative   - object can have only non-negative values
        - negative
        - nonpositive
        - comparable    - object.evalf() returns Number object.
        - irrational    - object value cannot be represented exactly by Rational

    Implementation note: assumption values are stored in
    ._assumption dictionary or are returned by getter methods (with
    property decorators) or are attributes of objects/classes.

    Examples:
    
        - True, when we are sure about a property. For example, when we are
        working only with real numbers:
        >>> from sympy import *
        >>> Symbol('x', real = True)
        x
        
        - False
        
        - None (if you don't know if the property is True or false)
    """

    def assume(self, **assumptions):
        """ Modify object assumptions in-situ.

        Usage examples:
          obj.assume(commutative = True,  # obj is in commutative center
                     positive = False,    # obj is non-negative
                     real = None          # assumption that obj is real will be removed
                     )
          obj.is_commutative              # check if object is commutative

        User is responsible for setting reasonable assumptions.
        """
        #XXX: ensure that assumptions like negative, positive, nonnegative, nonpositive are exclusive
        assumptions = self._assumptions
        for k, v in assumptions.items():
            if isinstance(v, (bool, int, long)):
                assumptions[k] = bool(v)
            elif v is None:
                try: del assumptions[k]
                except KeyError: pass
            else:
                raise ValueError,"assumption value for %r can be bool|int|long|None but got %s"\
                      % (k, type(v))
        return

    @property
    def is_commutative(self):
        assumptions = self._assumptions
        name = 'commutative'
        # for backward compatibility:
        try: return assumptions['is_'+name]
        except KeyError: pass
        #
        try: return assumptions[name]
        except KeyError: pass
        if self.is_real:
            assumptions[name] = True
            return True
        if hasattr(self, '_calc_'+name):
            a = assumptions[name] = getattr(self,'_calc_'+name)()
            return a
        return None
    
    @property
    def is_real(self):
        assumptions = self._assumptions
        name = 'real'
        # for backward compatibility:
        try: return assumptions['is_'+name]
        except KeyError: pass
        #
        try: return assumptions[name]
        except KeyError: pass
        if self.is_integer or self.is_positive or self.is_nonpositive:
            assumptions[name] = True
            return True
        if hasattr(self, '_calc_'+name):
            a = assumptions[name] = getattr(self,'_calc_'+name)()
            return a
        return None

    @property
    def is_positive(self):
        assumptions = self._assumptions
        name = 'positive'
        try: return assumptions[name]
        except KeyError: pass
        try:
            r = assumptions['nonpositive']
            if r is not False: raise KeyError
            assumptions[name] = True
            return True
        except KeyError: pass
        if hasattr(self, '_calc_'+name):
            a = assumptions[name] = getattr(self,'_calc_'+name)()
            return a
        return None
    
    @property
    def is_nonpositive(self):
        assumptions = self._assumptions
        name = 'nonpositive'
        try: return assumptions[name]
        except KeyError: pass
        try:
            r = assumptions['negative']
            if r is not True: raise KeyError
            assumptions[name] = True
            return True
        except KeyError: pass
        try:
            r = assumptions['positive']
            if r is not False: raise KeyError
            assumptions[name] = True
            return True
        except KeyError: pass
        if hasattr(self, '_calc_'+name):
            a = assumptions[name] = getattr(self,'_calc_'+name)()
            return a
        return None

    @property
    def is_negative(self):
        assumptions = self._assumptions
        name = 'negative'
        try: return assumptions[name]
        except KeyError: pass
        try:
            r = assumptions['nonnegative']
            if r is not False: raise KeyError
            assumptions[name] = True
            return True
        except KeyError: pass
        if hasattr(self, '_calc_'+name):
            a = assumptions[name] = getattr(self,'_calc_'+name)()
            return a
        return None
    
    @property
    def is_nonnegative(self):
        assumptions = self._assumptions
        name = 'nonnegative'
        try: return assumptions[name]
        except KeyError: pass
        try:
            r = assumptions['positive']
            if r is not True: raise KeyError
            assumptions[name] = True
            return True
        except KeyError: pass
        try:
            r = assumptions['negative']
            if r is not False: raise KeyError
            assumptions[name] = True
            return True
        except KeyError: pass
        if hasattr(self, '_calc_'+name):
            a = assumptions[name] = getattr(self,'_calc_'+name)()
            return a
        return None

