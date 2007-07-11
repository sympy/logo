
class AssumeMeths(object):
    """ Define default assumption methods.
    
    AssumeMeths should be used to derive Basic class only.

    All symbolic objects have assumption attributes that
    can be accessed via .is_<assumption name> attribute.
    Assumptions determine certain properties of symbolic
    objects. Assumptions can have 3 possible values: True, False, None.
    None is returned when it is impossible to say something
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
        - negative      - object can have only negative values
        - comparable    - object.evalf() returns Number object.
        - irrational    - object value cannot be represented exactly by Rational
        - unbounded     - object value is arbitrarily large
        - infinitesimal - object value is infinitesimal
        - order         - expression is not contained in Order(order).

    Example rules:

      positive=True|False -> negative=not positive, real=True
      positive=None -> negative=None
      unbounded=False|True -> bounded=not unbounded
      irrational=True -> real=True

    Exceptions:
      positive=negative=False for Zero() instance

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

    def _change_assumption(self, d, name, value, extra_msg = ''):
        default_assumptions = self.__class__.default_assumptions
        fixedvalue = default_assumptions.get(name, None)
        if value is None:
            oldvalue = d.pop(name, None)
        else:
            oldvalue = d.get(name, fixedvalue)
            if oldvalue is not None and  oldvalue != value and fixedvalue is not None:
                raise TypeError('%s: cannot change fixed assumption item from %s=%s to %s=%s%s'\
                                % (self.__class__.__name__, name, oldvalue, name, value, extra_msg))
            d[name] = value

    def assume(self, **assumptions):
        """ Modify object assumptions in-situ.

        Usage examples:
          obj.assume(commutative = True,  # obj is in commutative center
                     real = None          # assumption that obj is real will be removed
                     )
          obj.is_commutative              # check if object is commutative

        User is responsible for setting reasonable assumptions.
        """
        default_assumptions = self.__class__.default_assumptions
        for k,v in default_assumptions.items():
            if assumptions.has_key(k):
                nv = assumptions[k]
                if nv!=v:
                    raise TypeError("%s: assumption %r is fixed to %r for this class." \
                                    % (self.__class__.__name__,k,v))
            assumptions[k] = v
        d = self._assumptions = getattr(self, '_assumptions', {})
        def get_unset(name, default=None):
            if default_assumptions.has_key(name):
                return default_assumptions[name]
            return default
        while assumptions:
            k, v = assumptions.popitem()
            # obsolete, to be removed:
            if k.startswith('is_'):
                k = k[3:]
                assumptions[k] = v
                continue
            #
            extra_msg = ' (while changing %s)' % (k)
            if k=='order':
                v = self.Order(v)
            elif v is not None: v = bool(v)
            if k=='order':
                if v is None:
                    self._change_assumption(d, 'order', None)
                else:
                    self._change_assumption(d, 'order', v)
            elif k=='real':
                if v is None:
                    self._change_assumption(d, 'real', None)
                    self._change_assumption(d, 'positive', None, extra_msg)
                    self._change_assumption(d, 'negative', None, extra_msg)
                    self._change_assumption(d, 'irrational', None, extra_msg)
                    self._change_assumption(d, 'integer', None, extra_msg)
                else:
                    self._change_assumption(d, 'real', v)
                    if not v:
                        self._change_assumption(d, 'positive', False, extra_msg)
                        self._change_assumption(d, 'negative', False, extra_msg)
                        self._change_assumption(d, 'irrational', False, extra_msg)
                        self._change_assumption(d, 'integer', False, extra_msg)
            elif k=='positive':
                if v is None:
                    self._change_assumption(d, 'real', None, extra_msg)
                    self._change_assumption(d, 'positive', None)
                    self._change_assumption(d, 'negative', None, extra_msg)
                else:
                    self._change_assumption(d, 'positive', v)
                    self._change_assumption(d, 'negative', get_unset('negative',not v), extra_msg)
                    self._change_assumption(d, 'real', get_unset('real',True), extra_msg)
            elif k=='negative':
                if v is None:
                    assumptions['positive'] = None
                else:
                    assumptions['positive'] = get_unset('positive', not v)
            elif k=='bounded':
                if v is None:
                    self._change_assumption(d, 'bounded', None)
                    self._change_assumption(d, 'unbounded', None, extra_msg)
                    self._change_assumption(d, 'infinitesimal', None, extra_msg)
                else:
                    self._change_assumption(d, 'bounded', v)
                    self._change_assumption(d, 'unbounded', get_unset('unbounded', not v), extra_msg)
                    if not v:
                        self._change_assumption(d, 'infinitesimal', get_unset('infinitesimal', False), extra_msg)
            elif k=='unbounded':
                if v is None:
                    assumptions['bounded'] = None
                else:
                    assumptions['bounded'] = get_unset('bounded', not v)
            elif k=='infinitesimal':
                if v is None:
                    self._change_assumption(d, 'infinitesimal', None)
                else:
                    self._change_assumption(d, 'infinitesimal', v)
                    if v:
                        self._change_assumption(d, 'bounded', get_unset('bounded', True), extra_msg)
                        self._change_assumption(d, 'unbounded', get_unset('unbounded', False), extra_msg)
            elif k=='irrational':
                if v is None:
                    self._change_assumption(d, 'irrational', None)
                    self._change_assumption(d, 'real', None, extra_msg)
                else:
                    self._change_assumption(d, 'irrational', v)
                    assumptions['real'] = get_unset('real',True)
            elif k=='integer':
                if v is None:
                    self._change_assumption(d, 'integer', None)
                else:
                    self._change_assumption(d, 'integer', v)
                    assumptions['real'] = get_unset('real',True)
            elif k=='even':
                if v is None:
                    self._change_assumption(d, 'even', None)
                    self._change_assumption(d, 'odd', None)
                else:
                    self._change_assumption(d, 'even', v)
                    self._change_assumption(d, 'odd', not v, extra_msg)
                    assumptions['integer'] = get_unset('integer',True)
            elif k=='odd':
                if v is None:
                    self._change_assumption(d, 'odd', None)
                    self._change_assumption(d, 'even', None)
                else:
                    self._change_assumption(d, 'odd', v)
                    self._change_assumption(d, 'even', not v, extra_msg)
                    assumptions['integer'] = get_unset('integer',True)
            elif k=='commutative':
                if v is None:
                    self._change_assumption(d, 'commutative', None)
                    self._change_assumption(d, 'noncommutative', None, extra_msg)
                else:
                    self._change_assumption(d, 'commutative', v)
                    self._change_assumption(d, 'noncommutative', not v, extra_msg)
            elif k=='noncommutative':
                if v is None:
                    assumptions['commutative'] = None
                else:
                    assumptions['commutative'] = get_unset('commutative',not v)
            elif k in ['dummy','comparable']:
                if v is None:
                    self._change_assumption(d, k, None)
                else:
                    self._change_assumption(d, k, v)
            else:
                raise ValueError('unrecognized assumption item (%r:%r)' % (k,v))
        return

    def _eval_is_negative(self):
        r = self.is_positive
        if r is not None: return not r
        return

    def _eval_is_unbounded(self):
        r = self.is_bounded
        if r is not None: return not r
        return

    def _eval_is_odd(self):
        r = self.is_even
        if r is not None: return not r
        return

    def _eval_is_noncommutative(self):
        r = self.is_commutative
        if r is not None: return not r
        return

    def _assume_hashable_content(self):
        d = self._assumptions
        keys = d.keys()
        keys.sort()
        return tuple([(k+'=', d[k]) for k in keys])
