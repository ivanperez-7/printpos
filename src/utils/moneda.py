""" Módulo con clase `Moneda` para manejar cantidades monetarias. """
import operator
import re
from typing import Union


PRECISION = 2
OP_ERROR = lambda arg: TypeError(f'Segundo operando debe ser Moneda o numérico, no {type(arg)}.')

def _preparar_op_aritm(op):
    if isinstance(op, Moneda):
        return op.valor
    elif isinstance(op, (float, int)):
        return op
    else:
        raise OP_ERROR(op)

def _preparar_op_logico(op):
    if isinstance(op, Moneda):
        return op.safe_float
    elif isinstance(op, (float, int)):
        return round(op, PRECISION)
    else:
        raise OP_ERROR(op)


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
        return Moneda(-self.valor)
    
    def __repr__(self):
        return f'Moneda: {self.valor:,.{PRECISION}f} MXN'
    
    def __str__(self):
        return f'{self.valor:,.{PRECISION}f}'
    
    # =========================
    #  Operaciones aritméticas 
    # =========================
    def __realizar_op_aritm(self, op, operator):
        op_value = _preparar_op_aritm(op)
        result = operator(self.valor, op_value)
        return Moneda(result)
    
    def __add__(self, op):
        return self.__realizar_op_aritm(op, operator.add)
    
    def __radd__(self, op):
        return self.__realizar_op_aritm(op, operator.add)
    
    def __sub__(self, op):
        return self.__realizar_op_aritm(op, operator.sub)
    
    def __rsub__(self, op):
        return self.__realizar_op_aritm(op, lambda x,y: y-x)
    
    def __mul__(self, op):
        return self.__realizar_op_aritm(op, operator.mul)
    
    def __rmul__(self, op):
        return self.__realizar_op_aritm(op, operator.mul)
    
    def __truediv__(self, op):
        return self.__realizar_op_aritm(op, operator.truediv)
    
    # =====================
    #  Operaciones lógicas 
    # =====================
    def __comparar(self, op, operator) -> bool:
        op_value = _preparar_op_logico(op)
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
