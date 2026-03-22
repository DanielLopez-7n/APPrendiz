from django.test import TestCase
from django.db.utils import IntegrityError
from datetime import date
from programas.models import Programa
from fichas.models import Ficha

class FichasTests(TestCase):
    
    def setUp(self):
        """
        Preparamos los datos base: Un programa y una ficha real.
        """
        self.programa = Programa.objects.create(nombre='Analisis y Desarrollo de Software')
        
        self.ficha = Ficha.objects.create(
            numero='2999999',
            programa=self.programa,
            fecha_inicio=date(2023, 1, 1),
            fecha_fin=date(2024, 12, 31)
        )

    # 🟢 PRUEBA 1: Creación correcta del Programa
    def test_creacion_programa(self):
        programa_guardado = Programa.objects.get(nombre='Analisis y Desarrollo de Software')
        self.assertEqual(programa_guardado.nombre, 'Analisis y Desarrollo de Software')
        print("OK: Prueba 1 superada: El programa se crea correctamente.")

    # 🟢 PRUEBA 2: Creación y relación de la Ficha
    def test_creacion_ficha_y_relacion(self):
        ficha_guardada = Ficha.objects.get(numero='2999999')
        # Verificamos que la ficha se haya guardado y esté amarrada al programa correcto
        self.assertEqual(ficha_guardada.programa.nombre, 'Analisis y Desarrollo de Software')
        print("OK: Prueba 2 superada: La ficha se amarra perfectamente a su programa.")

    # 🟢 PRUEBA 3: El formato de texto (__str__)
    def test_representacion_string_ficha(self):
        # Probamos que en el panel de admin se vea bonito "Numero - Programa"
        texto_esperado = '2999999 - Analisis y Desarrollo de Software'
        self.assertEqual(str(self.ficha), texto_esperado)
        print("OK: Prueba 3 superada: El formato de lectura de la ficha es correcto.")

    # 🟢 PRUEBA 4: Bloqueo de Fichas Duplicadas (Restricción UNIQUE)
    def test_bloqueo_fichas_duplicadas(self):
        # Intentamos crear una ficha nueva pero con el MISMO número de la anterior
        with self.assertRaises(IntegrityError):
            Ficha.objects.create(
                numero='2999999', # ¡Este número ya existe!
                programa=self.programa,
                fecha_inicio=date(2024, 1, 1),
                fecha_fin=date(2025, 1, 1)
            )
        print("OK: Prueba 4 superada: El sistema prohíbe crear fichas con números repetidos.")

    # 🟢 PRUEBA 5: Eliminación en Cascada
    def test_eliminacion_cascada_programa(self):
        # Si el SENA decide borrar un programa completo de la base de datos...
        self.programa.delete()
        # ...las fichas asociadas a ese programa también deben desaparecer automáticamente
        cantidad_fichas = Ficha.objects.count()
        self.assertEqual(cantidad_fichas, 0)
        print("OK: Prueba 5 superada: La eliminación en cascada mantiene la base de datos limpia.")