"""
Does many simple operations with values that have units.
Takes advantage of Python's operator overloading to allow
you to write expressions with units in Python's regular 
interpreter.

>>> # Write units in several different ways
>>> 2*cm
>>> 2|cm
>>> cm(2) # for when operator precedence is hurting you

A common pitfall to avoid:
>>> 2|cm + 2|cm
Traceback (most recent call last):
  File "<console>", line 1, in <module>
TypeError: unsupported operand type(s) for +: '_Unit' and 'int'
>>> (2|cm) + (2|cm)  # or since this is +: 2*cm + 2*cm
4 cm

Python binds certain operators much higher than others.
Unfortunately there is no way to get around this other than
putting parenthesis everywhere or using the supported `cm()`
function syntax.
"""

import code

from operator import div, mul, add, sub

FORMATTED_OPERATORS = {
    div: '/',
    mul: '*',
    add: '+',
    sub: '-'
}

# length units
MIL = 'mil'
IN = 'in'
MM = 'mm'
CM = 'cm'

# temperature units
DEG_C = 'degC'
DEG_F = 'degF'
DEG_K = 'degK'

CONVERSION_FUNCTIONS = {
    # conversion from mils
    MIL: {
        IN: (lambda x: x * 0.001),
        MM: (lambda x: x * 0.0254),
        CM: (lambda x: x * 0.00254),
        MIL: (lambda x: x * 1.0),
    },
    # conversion from inches
    IN: {
        MIL: (lambda x: x * 1000),
        MM: (lambda x: x * 25.4),
        CM: (lambda x: x * 2.54),
        IN: (lambda x: x * 1.0),
    },
    # conversion from millimeters
    MM: {
        MIL: (lambda x: x * (1 / 0.0254)),
        IN: (lambda x: x * (1 / 25.4)),
        CM: (lambda x: x * 0.1),
        MM: (lambda x: x * 1.0),
    },
    # conversion from centimeters
    CM: {
        MIL: (lambda x: x * (1 / 0.00254)),
        IN: (lambda x: x * (1 / 2.54)),
        MM: (lambda x: x * 10),
        CM: (lambda x: x * 1.0),
    },
    # conversion from degrees Celsius
    DEG_C: {
        DEG_F: (lambda x: x * (9.0/5.0) + 32.0),
        DEG_K: (lambda x: x + 273.15),
    },
    # conversion from degrees Fahrenheit
    DEG_F: {
        DEG_C: (lambda x: (x - 32.0) * (5.0/9.0)),
        DEG_K: (lambda x: (x - 32.0) * (5.0/9.0) + 273.15),
    },
    # conversion from degrees Kelvin
    DEG_K: {
        DEG_C: (lambda x: x - 273.15),
        DEG_F: (lambda x: (x - 273.15) * (9.0/5.0) + 32.0),
    }
}


class IncompatibleUnits(Exception):
    def __init__(self, message, other_is_compatible=False):
        Exception.__init__(self, message)
        self.other_is_compatible = other_is_compatible


class UnitVar(object):

    def __init__(self, value, unit=None):
        if isinstance(value, UnitVar):
            unit = value.unit
            value = value.value
        
        self.value = value
        self.unit = unit

    def __repr__(self):
        if self.unit is None:
            return str(self.value)
        return "%s %s" % (self.value, self.unit)

    def __neg__(self):
        return UnitVar(-self.value, self.unit)
    def __pos__(self):
        return UnitVar(+self.value, self.unit)
    def __abs__(self):
        return UnitVar(abs(self.value), self.unit)
    def __invert__(self):
        return UnitVar(~self.value, self.unit)

    def __mul__(self, other):
        if isinstance(other, UnitVar):
            if other.unit is None:
                other = other.value
            else:
                return Expression([mul, self, other])
        return UnitVar(self.value * other, self.unit)
    def __div__(self, other):
        if isinstance(other, UnitVar):
            if other.unit is None:
                other = other.value
            else:
                return Expression([div, self, other])
        return UnitVar(self.value / other, self.unit)

    def __rmul__(self, other):
        if not isinstance(other, UnitVar) or other.unit is None:
            other = UnitVar(other)
            return other.__mul__(self)
        
        return Expression([mul, other, self])
    def __rdiv__(self, other):
        if not isinstance(other, UnitVar) or other.unit is None:
            other = UnitVar(other)
            return other.__div__(self)
        
        return Expression([div, other, self])

    def __add__(self, other):
        return self.__op__(add, other)
    def __sub__(self, other):
        return self.__op__(sub, other)
    def __radd__(self, other):
        return self.__op__(add, other, reverse=True)
    def __rsub__(self, other):
        return self.__op__(sub, other, reverse=True)

    def __op__(self, op, other, reverse=False):
        if not isinstance(other, UnitVar):
            other = UnitVar(other)
        
        try:
            value, other_value, unit = self._coerce_with(other)
        except IncompatibleUnits as e:
            if e.other_is_compatible:
                return NotImplemented
            if reverse:
                expr = [op, other, self]
            else:
                expr = [op, self, other]
            return Expression(expr)

        if reverse:
            return UnitVar(op(other_value, value), unit)
        else:
            return UnitVar(op(value, other_value), unit)

    def _coerce_with(self, other):
        converter = self._conversion_method(self.unit, other.unit)
        if converter:
            return self.value, converter(other.value), self.unit
        else:
            other_is_compatible = self._conversion_method(other.unit, self.unit)
            raise IncompatibleUnits("Incompatible units", other_is_compatible)

    def _conversion_method(self, from_, to):
        if from_ == to:
            return lambda x: x
        try:
            return CONVERSION_FUNCTIONS[to][from_]
        except KeyError:
            return None


class Expression(object):

    def __init__(self, ast):
        """
        ast is an array in the format [operator func, value 1, value 2]
        where value 1 and value 2 can either be values or another list
        in the same format
        """
        self.ast = ast

    def __repr__(self):
        return self.format(self.ast)[1:-1]

    def format(self, tree):
        if not isinstance(tree, list):
            return str(tree)
        
        op, v1, v2 = tree
        return "(%s %s %s)"%(self.format(v1), FORMATTED_OPERATORS[op], self.format(v2))


def unit_var_creator(unit):
    class _Unit(object):
        def __rmul__(self, other):
            return UnitVar(other, unit)
        def __ror__(self, other):
            return UnitVar(other, unit)
        def __call__(self, other):
            return UnitVar(other, unit)
    return _Unit()


mil = unit_var_creator(MIL)
in_ = unit_var_creator(IN)
mm = unit_var_creator(MM)
cm = unit_var_creator(CM)
degC = unit_var_creator(DEG_C)
degF = unit_var_creator(DEG_F)
degK = unit_var_creator(DEG_K)

if __name__ == "__main__":
    code.interact(local=locals())
