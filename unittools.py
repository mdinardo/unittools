from exceptions import TypeError, ZeroDivisionError

# units
MIL = 'mil'
IN = 'in'
MM = 'mm'
CM = 'cm'

# factors are in a from-to format
FACTORS = {
    # mils conversion factors
    MIL : {
        IN : 0.001,
        MM : 0.0254,
        CM : 0.00254,
        MIL : 1.0,
    } ,
    # inch conversion factors
    IN : {
        MIL : 1000,
        MM : 25.4,
        CM : 2.54,
        IN : 1.0,
    } ,
    # millimeter conversion factors
    MM : {
        MIL : (1 / 0.0254),
        IN : (1 / 25.4),
        CM : 0.1,
        MM : 1.0,
    } ,
    # centimeter conversion factors
    CM : {
        MIL : (1 / 0.00254),
        IN : (1 / 2.54),
        MM : 10,
        CM : 1.0,
    }
}

#########################################

def mil(x = 1):
    return UnitVar(x, MIL)

def inch(x = 1):
    return UnitVar(x, IN)

def mm(x = 1):
    return UnitVar(x, MM)

def cm(x = 1):
    return UnitVar(x, CM)

##########################################

class UnitVar(object):
    
    def __init__(self, value, unit):
        if _is_number(value):
            self.value = float(value)
            self.__unit = unit
        elif _is_UnitVar(value):
            # copy data from other UnitVar
            self.__unit = __unit
            self.__value = value.__value
            # Transform to new unit
            self._transform(value.unit)

    @property
    def unit(self):
        return self.__unit
    
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if _is_number(value):
            self.__value = value
            self.__value = value

    def __str__(self):
        return self.format(fmt='{0}{1}')
    
    def format(self, fmt=None):
        if fmt == None: 
            fmt = '{0}{1}'
        return fmt.format(self.__value, self.__unit)
    
    @staticmethod
    def _is_number(u):
        return isinstance(u, (int, float))

    @staticmethod
    def _is_UnitVar(u):
        return isinstance(u, UnitVar)

    """
    Transforms this UnitVar instance into the specified unit 'to_unit'

    This instance is returned to enable method chaining.
    """
    def _transform(self, to_unit):
        self.value = self.__value * FACTORS[ self.__unit ][ to_unit ]
        self.__unit = to_unit
        return self

    def to_mil(self):
        """
        Transforms this instance to mils.
        """
        return self._transform(MIL)
    
    def to_inch(self):
        """
        Transforms this instance to inches.
        """
        return self._transform(IN)
    
    def to_mm(self):
        """
        Transforms this instance to millimeters.
        """
        return self._transform(MM)
    
    def to_cm(self):
        """
        Transforms this instance to centimeters.
        """
        return self._transform(CM)
    
    ########################
   
    def _convert(self, to_unit):
        """
        Creates a new instance form this instance that is in the specified unit 'to_unit'
        """
        return UnitVar(self, to_unit)

    def mil(self, x):
        """
        Creates a new UnitVar instance with this instance's value converted to mils.
        """
        return self._convert(MIL)

    def inch(self, x):
        """
        Creates a new UnitVar instance with this instance's value converted to inches.
        """
        return self._convert(INCH)

    def mm(self, x):
        """
        Creates a new UnitVar instance with this instance's value converted to millimeters.
        """
        return self._convert(MM)

    def cm(self, x):
        """
        Creates a new UnitVar instance with this instance's value converted to centimeters.
        """
        return self._convert(CM)
   
    ######################################

    def __pos__(self):
        return self
    
    def __neg__(self):
        return UnitVar( - self.__value, self.__unit)

    def __add__(self, y):
        z = None
        if self._is_number(y):
            return UnitVar(self.value + y, self.__unit)
        elif self._is_UnitVar(y):
            z = y._convert(self.__unit)
            z.__value += self.__value
        return z

    def __radd__(self, x):
        z = None
        if self._is_number(x):
            z = UnitVar(x + self.value, self.__unit)
        return z

    def __sub__(self, y):
        z = None
        if self._is_number(y):
            z = UnitVar(self.value - y, self.__unit)
        elif self._is_UnitVar(y):
            z = y._convert(self.__unit)
            z.__value -= self.__value
        return z

    def __rsub__(self, x):
        z = None
        if self._is_number(x):
            z = UnitVar(x - self.value, self.__unit)
        return z

    def __mul__(self, y):
        z = None
        if self._is_number(y):
            z = UnitVar(self.value * y, self.__unit)
        return z

    def __rmul__(self, x):
        z = None
        if self._is_number(x):
            z = UnitVar(x * self.value, self.__unit)
        return z

    def __div__(self, y):
        z = None
        if self._is_number(y):
            if 0 == y:
                raise ZeroDivisionError('Cannot divide UnitVar by a constant value of zero')
            
            else:
                z = UnitVar(self.__value / y, self.__unit)
        return z

    def __rdiv__(self, x):
        z = None
        if self._is_number(x):
            if 0 == x:
                raise ZeroDivisionError('Cannot divide constant by a UnitVar with a magnitude of zero')
            else:
                z = UnitVar(x / self.__value, self.__unit)
        return z
