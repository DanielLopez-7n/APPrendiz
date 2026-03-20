from django.test import TestCase
from django.db.utils import IntegrityError
from empresas.models import Empresa

class EmpresasTests(TestCase):
    
    def setUp(self):
        """Preparamos una empresa de prueba"""
        self.empresa = Empresa.objects.create(
            nombre='SENA Empresa',
            nit='900123456-7',
            direccion='Calle 123 #45-67'
            # Si tu modelo pide teléfono obligatorio, agrégalo: telefono='3001234567'
        )

    # 🟢 PRUEBA 1: Creación
    def test_creacion_empresa(self):
        empresa_bd = Empresa.objects.get(nit='900123456-7')
        self.assertEqual(empresa_bd.nombre, 'SENA Empresa')
        print("✅ Prueba 1 superada: La empresa se crea correctamente.")

    # 🟢 PRUEBA 2: Actualización de datos
    def test_actualizacion_empresa(self):
        self.empresa.direccion = 'Carrera 9 #8-76'
        self.empresa.save()
        empresa_actualizada = Empresa.objects.get(nit='900123456-7')
        self.assertEqual(empresa_actualizada.direccion, 'Carrera 9 #8-76')
        print("✅ Prueba 2 superada: Los datos de la empresa se pueden actualizar.")

    # 🟢 PRUEBA 3: Formato de Lectura (__str__)
    def test_representacion_string_empresa(self):
        # Verifica que al imprimir la empresa, muestre el nombre
        self.assertTrue('SENA Empresa' in str(self.empresa))
        print("✅ Prueba 3 superada: El nombre de la empresa se formatea bien.")

    # 🟢 PRUEBA 4: Bloqueo de NIT duplicado
    def test_bloqueo_nit_duplicado(self):
        # Simulamos crear otra empresa con el mismo NIT
        with self.assertRaises(Exception): 
            Empresa.objects.create(
                nombre='Otra Empresa Copiona',
                nit='900123456-7', # ¡NIT que ya existe!
                direccion='Avenida Siempre Viva'
            )
        print("✅ Prueba 4 superada: El sistema prohíbe empresas con NIT repetido.")

    # 🟢 PRUEBA 5: Eliminación
    def test_eliminacion_empresa(self):
        self.empresa.delete()
        cantidad = Empresa.objects.count()
        self.assertEqual(cantidad, 0)
        print("✅ Prueba 5 superada: La empresa se elimina correctamente de la base de datos.")