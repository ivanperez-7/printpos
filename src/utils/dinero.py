""" Módulo con clase `Dinero` para manejar cantidades monetarias. """
import re
from typing import Union

PRECISION = 2


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
    
    def __bool__(self):
        return self.safe_float > 0.0
    
    def __float__(self):
        return self.safe_float
    
    def __add__(self, op) -> 'Dinero':
        if isinstance(op, Dinero):
            return Dinero(self.valor + op.valor)
        elif isinstance(op, (float, int)):
            return Dinero(self.valor + op)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __sub__(self, op) -> 'Dinero':
        if isinstance(op, Dinero):
            return Dinero(self.valor - op.valor)
        elif isinstance(op, (float, int)):
            return Dinero(self.valor - op)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __rsub__(self, op) -> 'Dinero':
        if isinstance(op, Dinero):
            return Dinero(op.valor - self.valor)
        elif isinstance(op, (float, int)):
            return Dinero(op - self.valor)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __neg__(self) -> 'Dinero':
        return Dinero(-self.valor)
    
    def __mul__(self, op) -> 'Dinero':
        if isinstance(op, Dinero):
            return Dinero(self.valor * op.valor)
        elif isinstance(op, (float, int)):
            return Dinero(self.valor * op)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __truediv__(self, op) -> 'Dinero':
        if isinstance(op, Dinero):
            return Dinero(self.valor / op.valor)
        elif isinstance(op, (float, int)):
            return Dinero(self.valor / op)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __eq__(self, op):
        if isinstance(op, Dinero):
            return self.safe_float == op.safe_float
        elif isinstance(op, (float, int)):
            return self.safe_float == round(op, PRECISION)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __ne__(self, op):
        if isinstance(op, Dinero):
            return self.safe_float != op.safe_float
        elif isinstance(op, (float, int)):
            return self.safe_float != round(op, PRECISION)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __lt__(self, op):
        if isinstance(op, Dinero):
            return self.safe_float < op.safe_float
        elif isinstance(op, (float, int)):
            return self.safe_float < round(op, PRECISION)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __le__(self, op):
        if isinstance(op, Dinero):
            return self.safe_float <= op.safe_float
        elif isinstance(op, (float, int)):
            return self.safe_float <= round(op, PRECISION)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __gt__(self, op):
        if isinstance(op, Dinero):
            return self.safe_float > op.safe_float
        elif isinstance(op, (float, int)):
            return self.safe_float > round(op, PRECISION)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __ge__(self, op):
        if isinstance(op, Dinero):
            return self.safe_float >= op.safe_float
        elif isinstance(op, (float, int)):
            return self.safe_float >= round(op, PRECISION)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __repr__(self):
        return f'Dinero: {self.safe_float:,.2f} MXN'
    
    def __str__(self):
        return f'{self.safe_float:,.2f}'
