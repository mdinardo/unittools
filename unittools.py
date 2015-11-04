from exceptions import TypeError, ZeroDivisionError

# length units
MIL = 'mil'
IN = 'in'
MM = 'mm'
CM = 'cm'

# temperature units
DEG_C = 'degC'
DEG_F = 'degF'
DEG_K = 'degK'

class ConverterMapException(Exception):
    """
    ConverterException

    This exception is raised if a conversion between
    two units does not exist in the converters map
    """
    def __init__(self, message, from_unit, to_unit=None):
        super(ConverterMapException, self).__init__(message)
        self.message = message
        self.from_unit = from_unit
        self.to_unit = to_unit

########################################

# converters are in a from-to format
CONVERTER_MAP = {

    # conversion from mils
    MIL : {
        IN : (lambda x: x * 0.001),
        MM : (lambda x: x * 0.0254),
        CM : (lambda x: x * 0.00254),
        MIL : (lambda x: x * 1.0),
    } ,
    # conversion from inches
    IN : {
        MIL : (lambda x: x * 1000),
        MM : (lambda x: x * 25.4),
        CM : (lambda x: x * 2.54),
        IN : (lambda x: x * 1.0),
    } ,
    # conversion from millimeters
    MM : {
        MIL : (lambda x: x * (1 / 0.0254)),
        IN : (lambda x: x * (1 / 25.4)),
        CM : (lambda x: x * 0.1),
        MM : (lambda x: x * 1.0),
    } ,
    # conversion from centimeters
    CM : {
        MIL : (lambda x: x * (1 / 0.00254)),
        IN : (lambda x: x * (1 / 2.54)),
        MM : (lambda x: x * 10),
        CM : (lambda x: x * 1.0),
    },

    # conversion from degrees Celsius
    DEG_C : {
        DEG_F : (lambda x: x * (9.0/5.0) + 32.0),
        DEG_K : (lambda x: x + 273.15),
    },

    # conversion from degrees Fahrenheit
    DEG_F : {
        DEG_C : (lambda x: (x - 32.0) * (5.0/9.0)),
        DEG_K : (lambda x: (x - 32.0) * (5.0/9.0) + 273.15),
    },

    # conversion from degrees Kelvin
    DEG_K : {
        DEG_C : (lambda x: x - 273.15),
        DEG_F : (lambda x: (x - 273.15) * (9.0/5.0) + 32.0),
    },
}

def __get_converter(from_unit, to_unit):
    unit_map = CONVERTER_MAP.get(from_unit, None)
    
    if None == unit_map:
        # 1.) Throw a KeyError? 2.) exit function
        raise ConverterMapException(
                'Unit not convertable.',
                from_unit )
    
    converter = unit_map.get(to_unit, None)

    if None == converter:
        raise ConverterMapException(
                'Converter missing.',
                from_unit,
                to_unit)
    
    return converter

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
    """
    UnitVar

    A class that enables mixed-unit arithmetic.

    Arithmetic operations: 
        - addition (add, radd, iadd)
        - subtraction (sub, rsub, isub)
        - multiplication (mul, rmul, imul)
        - division (div, rdiv, idiv)
    
    Arithmetic rules:
        (*) Unless otherwise specified, mixed-unit arithemtic requires that
        a converter exists between the two units.  If a required converter
        does not exist, a ConverterMapException is raised.

        Addition
            1.) (scalar) + (UnitVar_A)
                Produces a UnitVar with a value of (scalar + UnitVar_A.value)
                and the unit of UnitVar_A
            2.) (UnitVar_A) + (UnitVar_B)   (same units)
                Produces a UnitVar with the value of 
                    (UnitVar_A.value + UnitVar_B.value)
                and the unit is conserved.
            3.) (UnitVar_A) + (UnitVar_B)   (mixed units)
                UnitVar_B is converted to the unit of UnitVar_A,
                and then case 2.) is applied.
                The result is in the same unit as UnitVar_A.

        Subtraction
            1.) (scalar) - (UnitVar_A)
                Produces a UnitVar with a value of (scalar - UnitVar_A.value)
                and the unit of UnitVar_A.
            2.) (UnitVar_A) - (UnitVar_B)   (same units)
                Produces a UnitVar with the value of 
                    (UnitVar_A.value - UnitVar_B.value)
                and the unit is conserved.
            3.) (UnitVar_A) - (UnitVar_B)   (mixed units)
                UnitVar_B is converted to the unit of UnitVar_A,
                and then case 2.) is applied.
                The result is in the same unit as UnitVar_A.

        Multiplication
            1.) (scalar) * (UnitVar_A)
                Produces a UnitVar with a value of (scalar * UnitVar_A.value)
                and the unit of UnitVar_A.
            2.) (UnitVar_A) * (UnitVar_B)
                Operation not permitted.

        Division
            1.) (scalar) / (UnitVar_A)
                Produces a UnitVar with a value of (scalar / UnitVar_A.value)
                and the unit of UnitVar_A.
            2.) (UnitVar_A) / (scalar)
                Produces a UnitVar with a value of (UnitVar_A.value / scalar)
                and the unit of UnitVar_A.
            3.) (UnitVar_A) / (UnitVar_B) 
                Operation not permitted.
    """
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
    
    def copy(self):
        return UnitVar(self.__value, self.__unit)
        
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

    def _transform(self, to_unit):
        """
        Transforms this UnitVar instance into the specified unit 'to_unit'

        This instance is returned to enable method chaining.
        """
        if to_unit != self.__unit
            converter = __get_converter(self.__unit, to_unit)
            self.__value = converter(self.__value)
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

    def __iadd__(self, y):
        if self._is_number(y):
            self.__value += y
        elif self._is_UnitVar(y):
            y = y.convert(self.__unit)
            self.__value += y.value
        else:
            pass
        return self

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
    
    def __isub__(self, y):
        if self._is_number(y):
            self.__value -= y
        elif self._is_UnitVar(y):
            y = y.convert(self.__unit)
            self.__value -= y.value
        else:
            pass
        return self

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
    
    def __imul__(self, y):
        if self._is_number(y):
            self.__value *= y
        else:
            pass
        return self
    
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

    def __idiv__(self, y):
        if self._is_number(y):
            if 0 == y:
                raise ZeroDivisionError('Cannot divide UnitVar by a constant value of zero')
            else:
                self.__value /= y
        else:
            pass
        return self
