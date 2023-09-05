""" Módulo con clase `Moneda` para manejar cantidades monetarias. """
import operator
import re
from typing import Union


PRECISION = 2
OP_ERROR = lambda arg: TypeError(f"Segundo operando debe ser Moneda o numérico, no '{arg.__class__.__name__}'.")


class Moneda:
    """ Clase para manejar cantidades monetarias
        con un máximo de dos números decimales. """
    def __init__(self, inicial: Union[int, float, str, 'Moneda'] = None):
        if inicial is None:
            self.valor = 0.0
        elif isinstance(inicial, Moneda):
            self.valor = inicial.valor
        elif isinstance(inicial, (int, float)):
            self.valor = float(inicial)
        elif isinstance(inicial, str):
            self.valor = float(re.sub(r'[$, ]', '', inicial))
        else:
            raise TypeError('Valor inicial no tiene ningún tipo apropiado.')
    
    @property
    def safe_float(self):
        return round(self.valor, PRECISION) + 0.0
    
    @classmethod
    @property
    def cero(cls):
        """ Forma explícita de generar valor cero. """
        return cls(0.)
    
    @staticmethod
    def sum(_iter) -> 'Moneda':
        """ Invoca función nativa `sum` con parámetro `start=Moneda.cero`. """
        return sum(_iter, start=Moneda.cero)
    
    # =====================
    #  Operaciones unarias 
    # =====================
    def __bool__(self):
        return self.safe_float > 0.0
    
    def __float__(self):
        return self.safe_float
    
    def __neg__(self):
        return self.__class__(-self.valor)
    
    def __repr__(self):
        return f'Moneda: {self.safe_float:,.{PRECISION}f} MXN'
    
    def __str__(self):
        return f'{self.safe_float:,.{PRECISION}f}'
    
    # =========================
    #  Operaciones aritméticas 
    # =========================
    def __op_aritm(self, op, operator):
        if isinstance(op, Moneda):
            op_value = op.valor
        elif isinstance(op, (float, int)):
            op_value = op
        else:
            raise OP_ERROR(op)
        result = operator(self.valor, op_value)
        return self.__class__(result)
    
    def __add__(self, op):
        return self.__op_aritm(op, operator.add)
    
    def __sub__(self, op):
        return self.__op_aritm(op, operator.sub)
    
    def __rsub__(self, op):
        return -self.__sub__(op)
    
    def __mul__(self, op):
        return self.__op_aritm(op, operator.mul)
    
    def __truediv__(self, op):
        return self.__op_aritm(op, operator.truediv)
    
    __radd__ = __add__
    __rmul__ = __mul__
    
    # =====================
    #  Operaciones lógicas 
    # =====================
    def __comparar(self, op, operator) -> bool:
        if isinstance(op, Moneda):
            op_value = op.safe_float
        elif isinstance(op, (float, int)):
            op_value = round(op, PRECISION)
        else:
            raise OP_ERROR(op)
        return operator(self.safe_float, op_value)
    
    def __eq__(self, op):
        return self.__comparar(op, operator.eq)
    
    def __ne__(self, op):
        return self.__comparar(op, operator.ne)
    
    def __lt__(self, op):
        return self.__comparar(op, operator.lt)
    
    def __le__(self, op):
        return self.__comparar(op, operator.le)
    
    def __gt__(self, op):
        return self.__comparar(op, operator.gt)
    
    def __ge__(self, op):
        return self.__comparar(op, operator.ge)
