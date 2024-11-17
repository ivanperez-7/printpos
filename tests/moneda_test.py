import unittest

from core import Moneda


class TestMoneda(unittest.TestCase):
    def test_inicializacion(self):
        """ Test para la inicialización de un objeto Moneda """
        
        # Inicialización sin parámetros (debería ser 0.0)
        moneda = Moneda()
        self.assertEqual(float(moneda), 0.0)
        
        # Inicialización con un valor numérico
        moneda = Moneda(100.5)
        self.assertEqual(float(moneda), 100.5)
        
        # Inicialización con un valor en string (con formato)
        moneda = Moneda("$50.50")
        self.assertEqual(float(moneda), 50.50)
        
        # Inicialización con un valor en string sin formato
        moneda = Moneda("1,000.99")
        self.assertEqual(float(moneda), 1000.99)

    def test_repr(self):
        """ Test para el método __repr__ """
        moneda = Moneda(50.5)
        self.assertEqual(repr(moneda), 'Moneda: 50.50 MXN')
        
        moneda = Moneda(1000.11999994812)
        self.assertEqual(repr(moneda), 'Moneda: 1,000.12 MXN')

    def test_str(self):
        """ Test para el método __str__ """
        moneda = Moneda(50.5)
        self.assertEqual(str(moneda), '50.50')
        
        moneda = Moneda(1000.12345)
        self.assertEqual(str(moneda), '1,000.12')

    def test_operaciones_aritmeticas(self):
        """ Test para las operaciones aritméticas """
        
        moneda1 = Moneda(50.5)
        moneda2 = Moneda(20.5)
        
        # Suma
        resultado = moneda1 + moneda2
        self.assertEqual(float(resultado), 71.0)
        
        # Resta
        resultado = moneda1 - moneda2
        self.assertEqual(float(resultado), 30.0)
        
        # Multiplicación
        resultado = moneda1 * 2
        self.assertEqual(float(resultado), 101.0)
        
        # División
        resultado = moneda1 / 2
        self.assertEqual(float(resultado), 25.25)

    def test_operaciones_unarias(self):
        """ Test para las operaciones unarias """
        
        moneda = Moneda(50.5)
        
        # Negación
        resultado = -moneda
        self.assertEqual(float(resultado), -50.5)
        
        # Redondeo
        resultado = round(moneda, 1)
        self.assertEqual(float(resultado), 50.5)
        
        # Conversión a entero
        resultado = int(moneda)
        self.assertEqual(resultado, 50)
        
        # Conversión a flotante
        resultado = float(moneda)
        self.assertEqual(resultado, 50.5)

    def test_comparaciones(self):
        """ Test para las comparaciones entre Moneda y otros tipos numéricos """
        
        moneda = Moneda(50.5)
        
        # Comparaciones con números
        self.assertTrue(moneda > 30)
        self.assertTrue(moneda < 100)
        self.assertTrue(moneda == 50.5)
        self.assertFalse(moneda != 50.5)
        self.assertTrue(moneda >= 50)
        self.assertTrue(moneda <= 50.5)

    def test_suma_iterable(self):
        """ Test para la suma de un iterable con Moneda.sum() """
        
        valores = [10.0, 20.0, 30.0]
        resultado = Moneda.sum(valores)
        self.assertEqual(float(resultado), 60.0)

    def test_bool(self):
        """ Test para la conversión a tipo booleano """
        
        moneda_positiva = Moneda(50.5)
        moneda_negativa = Moneda(0.0)
        
        self.assertTrue(bool(moneda_positiva))
        self.assertFalse(bool(moneda_negativa))

    def test_cero(self):
        """ Test para la propiedad Moneda.cero """
        
        # Verificar que Moneda.cero devuelve el valor 0.0
        cero = Moneda.cero
        self.assertEqual(float(cero), 0.0)
        
        # Verificar que la representación es correcta
        self.assertEqual(repr(cero), 'Moneda: 0.00 MXN')


if __name__ == '__main__':
    unittest.main()
