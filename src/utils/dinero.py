""" Módulo con clase `Dinero` para manejar cantidades monetarias. """
import operator
import re
from typing import Union


PRECISION = 2
OP_ERROR = lambda arg: TypeError(f'Segundo operando debe ser Dinero o numérico, no {type(arg)}.')

def _preparar_op_aritm(op):
    if isinstance(op, Dinero):
        return op.valor
    elif isinstance(op, (float, int)):
        return op
    else:
        raise OP_ERROR(op)

def _preparar_op_logico(op):
    if isinstance(op, Dinero):
        return op.safe_float
    elif isinstance(op, (float, int)):
        return round(op, PRECISION)
    else:
        raise OP_ERROR(op)


class Dinero:
    """ Clase para manejar cantidades monetarias
        con un máximo de dos números decimales. """
    def __init__(self, inicial: Union[int, float, str, 'Dinero'] = None):
        if inicial is None:
            self.valor = 0.0
        elif isinstance(inicial, Dinero):
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
    def sum(_iter) -> 'Dinero':
        """ Invoca función nativa `sum` con parámetro `start=Dinero.cero`. """
        return sum(_iter, start=Dinero.cero)
    
    # =====================
    #  Operaciones unarias 
    # =====================
    def __bool__(self):
        return self.safe_float > 0.0
    
    def __float__(self):
        return self.safe_float
    
    def __neg__(self):
        return Dinero(-self.valor)
    
    def __repr__(self):
        return f'Dinero: {self.safe_float:,.2f} MXN'
    
    def __str__(self):
        return f'{self.safe_float:,.2f}'
    
    # =========================
    #  Operaciones aritméticas 
    # =========================
    def __realizar_op_aritm(self, op, operator, reverse = False):
        op_value = _preparar_op_aritm(op)
        if not reverse:
            result_value = operator(self.valor, op_value) 
        else:
            result_value = operator(op_value, self.valor)
        return Dinero(result_value)
    
    def __add__(self, op):
        return self.__realizar_op_aritm(op, operator.add)
    
    def __radd__(self, op):
        return self.__realizar_op_aritm(op, operator.add, reverse=True)
    
    def __sub__(self, op):
        return self.__realizar_op_aritm(op, operator.sub)
    
    def __rsub__(self, op):
        return self.__realizar_op_aritm(op, operator.sub, reverse=True)
    
    def __mul__(self, op):
        return self.__realizar_op_aritm(op, operator.mul)
    
    def __rmul__(self, op):
        return self.__realizar_op_aritm(op, operator.mul, reverse=True)
    
    def __truediv__(self, op):
        return self.__realizar_op_aritm(op, operator.truediv)
    
    def __rtruediv__(self, op):
        return self.__realizar_op_aritm(op, operator.truediv, reverse=True)
    
    # =====================
    #  Operaciones lógicas 
    # =====================
    def __comparar(self, op, operator):
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
