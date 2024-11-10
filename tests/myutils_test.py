import unittest

from PySide6.QtCore import QDateTime

from utils.myutils import *


class TestUtilidades(unittest.TestCase):

    def test_clamp(self):
        """ Test para la función clamp """
        self.assertEqual(clamp(5, 1, 10), 5)   # Dentro del rango
        self.assertEqual(clamp(0, 1, 10), 1)   # Menor que el mínimo
        self.assertEqual(clamp(15, 1, 10), 10) # Mayor que el máximo
        self.assertEqual(clamp(5, 5, 5), 5)    # Igual al valor límite

    def test_chunkify(self):
        """ Test para la función chunkify """
        self.assertEqual(chunkify([1, 2, 3, 4, 5, 6], 2), [[1, 2], [3, 4], [5, 6]])
        self.assertEqual(chunkify([1, 2, 3], 2), [[1, 2], [3]])
        self.assertEqual(chunkify([], 2), [])
        self.assertEqual(chunkify([1, 2, 3], 5), [[1, 2, 3]])

    def test_daysTo(self):
        """ Test para la función daysTo """
        self.assertEqual(daysTo(0), 'hoy')
        self.assertEqual(daysTo(1), 'hace un día')
        self.assertEqual(daysTo(3), 'hace 3 días')
        self.assertEqual(daysTo(7), 'hace una semana')
        self.assertEqual(daysTo(14), 'hace 2 semanas')
        self.assertEqual(daysTo(30), 'hace 1 mes')
        self.assertEqual(daysTo(365), 'hace 1 año')
        self.assertEqual(daysTo(1000), 'hace 2 años')
        self.assertEqual(daysTo(-1), 'Invalid input')

    def test_unidecode(self):
        """ Test para la función unidecode """
        self.assertEqual(unidecode('Pérez'), 'perez')
        self.assertEqual(unidecode('Álvaro'), 'alvaro')
        self.assertEqual(unidecode('Café'), 'cafe')

    def test_stringify_float(self):
        """ Test para la función stringify_float """
        self.assertEqual(stringify_float(1234.56), '1,234.56')
        self.assertEqual(stringify_float(1234), '1,234')
        self.assertEqual(stringify_float(1000), '1,000')
        self.assertEqual(stringify_float(0), '0')

    def test_son_similar(self):
        """ Test para la función son_similar """
        self.assertTrue(son_similar('Pérez', 'perez'))
        self.assertTrue(son_similar('Álvaro', 'alvaro'))
        self.assertFalse(son_similar('nada', 'cafe'))
        self.assertFalse(son_similar('Python', 'java'))

    def test_exportarXlsx(self):
        """ Test para la función exportarXlsx """
        # Este test crea un archivo, por lo que se debe verificar que el archivo existe después de la exportación
        ruta = 'test.xlsx'
        titulos = ['Nombre', 'Edad', 'Ciudad']
        datos = [('Juan', 30, 'México'), ('Ana', 28, 'Colombia')]
        
        exportarXlsx(ruta, titulos, datos)

        # Verifica que el archivo ha sido creado
        import os
        self.assertTrue(os.path.exists(ruta))

        # Limpia el archivo después de la prueba
        os.remove(ruta)


if __name__ == '__main__':
    unittest.main()
