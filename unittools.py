from exceptions import TypeError, ZeroDivisionError

# units
MIL = 'mil'
IN = 'in'
MM = 'mm'
CM = 'cm'

# mils conversion factors
MIL2IN = 0.001
MIL2MM = 0.0254
MIL2CM = 0.00254 

# inch conversion factors
IN2MIL = 1000
IN2MM = 25.4
IN2CM = 2.54

# millimeter conversion factors
MM2MIL = (1 / 0.0254)
MM2IN = (1 / 25.4)
MM2CM = 0.1

# centimeter conversion factors
CM2MIL = (1 / 0.00254)
CM2IN = (1 / 2.54)
CM2MM = 10

def _is_number(u):
    return isinstance(u, (int, float))

def _is_unit(u):
    return isinstance(u, UnitVar)

def __converter(func):
    def create_or_convert(x = 1):
        unit, conversions = func(x)
        if _is_number(x):
            return UnitVar(x, unit)
        elif _is_unit(x):
            return UnitVar(x.value * conversions[x.unit], unit)
    return create_or_convert

@__converter
def mil(x):
    conversions = {
        MIL : 1.0,
        IN : IN2MIL,
        MM : MM2MIL,
        CM : CM2MIL
    }
    return (MIL, conversions)  

@__converter
def inch(x):
    conversions = {
        MIL : MIL2IN,
        IN : 1.0,
        MM : MM2IN,
        CM : CM2IN
    }
    return (IN, conversions)

@__converter
def mm(x):
    conversions = {
        MIL : MIL2MM,
        IN : IN2MM,
        MM : 1.0,
        CM : CM2MM
    }
    return (MM, conversions)

@__converter
def cm(x):
    conversions = {
        MIL : MIL2CM,
        IN : IN2CM,
        MM : MM2CM,
        CM : 1.0
    }
    return (CM, conversions)

# maps a unit to a converter to that unit
CONVERTERS = {
    MIL : mil,
    IN : inch,
    MM : mm,
    CM : cm
}

class UnitVar:
    
    def __init__(self, value, unit):
        if _is_number(value):
            self.value = value
            self.unit = unit

        elif UnitVar._is_unit(value):
            pass
    
    def __str__(self):
        return self.format(fmt='{0}{1}')
    
    def format(self, fmt=None):
        if fmt == None: 
            fmt = '{0}{1}'
        return fmt.format(self.value, self.unit)

    def mil(self):
        return mil(self)

    def inch(self):
        return inch(self)

    def mm(self):
        return mm(self)

    def cm(self):
        return cm(self)

    def __add__(self, y):
        if _is_number(y):
            return UnitVar(self.value + y, self.unit)
        elif _is_unit(y):
            c = CONVERTERS[self.unit]
            y = c(y)
            return UnitVar(self.value + y.value, self.unit)

    def __radd__(self, x):
        if _is_number(x):
            return UnitVar(x + self.value, self.unit)

    def __sub__(self, y):
        if _is_number(y):
            return UnitVar(self.value - y, self.unit)
        elif _is_unit(y):
            c = CONVERTERS[self.unit]
            y = c(y)
            return UnitVar(self.value - y.value, self.unit)

    def __rsub__(self, x):
        if _is_number(x):
            return UnitVar(x - self.value, self.unit)

    def __mul__(self, y):
        if _is_number(y):
            return UnitVar(self.value * y, self.unit)

    def __rmul__(self, x):
        if _is_number(x):
            return UnitVar(x * self.value, self.unit)

    def __div__(self, y):
        if _is_number(y):
            if 0 == y:
                raise ZeroDivisionError('Cannot divide UnitVar by a constant value of zero')
            
            else:
                return UnitVar(self.value / y, self.unit)

    def __rdiv__(self, x):
        if _is_number(x):
            if 0 == x:
                raise ZeroDivisionError('Cannot divide constant by a UnitVar with a magnitude of zero')
            else:
                return UnitVar(x / self.value, self.unit)

