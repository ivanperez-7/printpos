""" Módulo con clase `Dinero` para manejar cantidades monetarias. """
PRECISION = 2

class Dinero:
    """ Clase para manejar cantidades monetarias
        con un máximo de dos números decimales. """
    def __init__(self, inicial: float = None):
        self.valor = inicial or 0.0
    
    @property
    def safe_float(self):
        return round(self.valor, PRECISION)
    
    @classmethod
    @property
    def cero(cls):
        """ Forma explícita de generar valor cero. """
        return cls(0.)
    
    def __add__(self, op):
        if isinstance(op, Dinero):
            return Dinero(self.valor + op.valor)
        elif isinstance(op, (float, int)):
            return Dinero(self.valor + op)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __sub__(self, op):
        if isinstance(op, Dinero):
            return Dinero(self.valor - op.valor)
        elif isinstance(op, (float, int)):
            return Dinero(self.valor - op)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __rsub__(self, op):
        if isinstance(op, Dinero):
            return Dinero(op.valor - self.valor)
        elif isinstance(op, (float, int)):
            return Dinero(op - self.valor)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __mul__(self, op):
        if isinstance(op, Dinero):
            return Dinero(self.valor * op.valor)
        elif isinstance(op, (float, int)):
            return Dinero(self.valor * op)
        else:
            raise TypeError('Segundo operando debe ser Dinero o numérico (int o float).')
    
    def __truediv__(self, op):
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
        return f'{self.safe_float:,.2f}'
