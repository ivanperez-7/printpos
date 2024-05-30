""" Módulo con clase `Moneda` para manejar cantidades monetarias. """
import operator
import re


class useless(type):
    """ Para habilitar `Moneda.cero`. """
    @property
    def cero(cls):
        return cls(0.)

class Moneda(metaclass=useless):
    """ Clase para manejar cantidades monetarias
        con un máximo de dos números decimales. """
    PRECISION = 2
    
    def __init__(self, inicial = None):
        if inicial is None:
            self.valor = 0.0
        elif isinstance(inicial, str):
            self.valor = re.sub(r'[$, ]', '', inicial)
        else:
            self.valor = inicial
    
    @property
    def valor(self):
        return self._valor + 0.0
    
    @valor.setter
    def valor(self, arg):
        self._valor = round(float(arg), self.PRECISION)
    
    @staticmethod
    def sum(iter_) -> 'Moneda':
        """ Invoca función nativa `sum` con parámetro `start=Moneda.cero`. """
        return sum(iter_, start=Moneda.cero)
    
    # =====================
    #  Operaciones unarias 
    # =====================
    def __bool__(self):
        return self.valor > 0.0
    
    def __int__(self):
        return int(self.valor)
    
    def __float__(self):
        return self.valor
    
    def __round__(self, ndigits):
        return round(self.valor, ndigits)
    
    def __neg__(self):
        return self.__class__(-self.valor)
    
    def __repr__(self):
        return f'Moneda: {self.valor:,.{self.PRECISION}f} MXN'
    
    def __str__(self):
        return f'{self.valor:,.{self.PRECISION}f}'
    
    # =========================
    #  Operaciones aritméticas 
    # =========================
    def _arit_op(self, other, operation) -> 'Moneda':
        if isinstance(other, Moneda):
            other = other.valor
        return self.__class__(operation(self.valor, other))
        
    def __add__(self, other):
        return self._arit_op(other, operator.add)
    
    def __sub__(self, other):
        return self._arit_op(other, operator.sub)
    
    def __rsub__(self, other):
        return -self.__sub__(other)
    
    def __mul__(self, other):
        return self._arit_op(other, operator.mul)
    
    def __truediv__(self, other):
        return self._arit_op(other, operator.truediv)
    
    __radd__ = __add__
    __rmul__ = __mul__
    
    # =====================
    #  Operaciones lógicas 
    # =====================
    def _bool_op(self, other, operation) -> bool:
        return operation(self.valor, round(other, self.PRECISION))
        
    def __eq__(self, other):
        return self._bool_op(other, operator.eq)
    
    def __ne__(self, other):
        return self._bool_op(other, operator.ne)
    
    def __lt__(self, other):
        return self._bool_op(other, operator.lt)
    
    def __le__(self, other):
        return self._bool_op(other, operator.le)
    
    def __gt__(self, other):
        return self._bool_op(other, operator.gt)
    
    def __ge__(self, other):
        return self._bool_op(other, operator.ge)
