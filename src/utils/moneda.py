""" Módulo con clase `Moneda` para manejar cantidades monetarias. """
import re
from typing import SupportsFloat


PRECISION = 2

class Moneda:
    """ Clase para manejar cantidades monetarias
        con un máximo de dos números decimales. """
    def __init__(self, inicial: SupportsFloat = None):
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
    def valor(self, arg: SupportsFloat):
        self._valor = round(float(arg), PRECISION)
    
    @classmethod
    @property
    def cero(cls):
        """ Forma explícita de generar valor cero. """
        return cls(0.)
    
    @staticmethod
    def sum(iter_) -> 'Moneda':
        """ Invoca función nativa `sum` con parámetro `start=Moneda.cero`. """
        return sum(iter_, start=Moneda.cero)
    
    # =====================
    #  Operaciones unarias 
    # =====================
    def __bool__(self):
        return self.valor > 0.0
    
    def __float__(self):
        return self.valor
    
    def __round__(self, ndigits):
        return round(self.valor, ndigits)
    
    def __neg__(self):
        return self.__class__(-self.valor)
    
    def __repr__(self):
        return f'Moneda: {self.valor:,.{PRECISION}f} MXN'
    
    def __str__(self):
        return f'{self.valor:,.{PRECISION}f}'
    
    # =========================
    #  Operaciones aritméticas 
    # =========================
    def __add__(self, op):
        return self.__class__(self.valor + op)
    
    def __sub__(self, op):
        return self.__class__(self.valor - op)
    
    def __rsub__(self, op):
        return -self.__sub__(op)
    
    def __mul__(self, op):
        return self.__class__(self.valor * op)
    
    def __truediv__(self, op):
        return self.__class__(self.valor / op)
    
    __radd__ = __add__
    __rmul__ = __mul__
    
    # =====================
    #  Operaciones lógicas 
    # =====================
    def __eq__(self, op):
        return self.valor == round(op, PRECISION)
    
    def __ne__(self, op):
        return self.valor != round(op, PRECISION)
    
    def __lt__(self, op):
        return self.valor < round(op, PRECISION)
    
    def __le__(self, op):
        return self.valor <= round(op, PRECISION)
    
    def __gt__(self, op):
        return self.valor > round(op, PRECISION)
    
    def __ge__(self, op):
        return self.valor >= round(op, PRECISION)
