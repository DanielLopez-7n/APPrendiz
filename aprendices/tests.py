from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from aprendices.models import Aprendiz
from fichas.models import Ficha
from programas.models import Programa
from datetime import date

class AprendicesTests(TestCase):
    
    def setUp(self):
        """
        Preparamos los datos base: Usuario -> Programa -> Ficha -> Aprendiz
        """
        # 1. Creamos la cuenta de usuario (Autenticación)
        self.user = User.objects.create_user(
            username='100200300', 
            password='Password123', 
            first_name='Carlos', 
            last_name='Perez'
        )
        
        # 2. Creamos el Programa y la Ficha
        self.programa = Programa.objects.create(nombre='ADSO')
        self.ficha = Ficha.objects.create(
            numero='2999999', 
            programa=self.programa, 
            fecha_inicio=date(2023, 1, 1), 
            fecha_fin=date(2024, 12, 31)
        )
        
        # 3. Creamos el perfil de Aprendiz
        self.aprendiz = Aprendiz.objects.create(
            usuario=self.user, 
            documento='100200300', 
            telefono='3100000000', 
            numero_ficha=self.ficha
        )

    # 🟢 PRUEBA 1: Verificación de Creación del Perfil
    def test_creacion_aprendiz_exitosa(self):
        aprendiz_bd = Aprendiz.objects.get(documento='100200300')
        # Comprobamos que guardó el teléfono correctamente
        self.assertEqual(aprendiz_bd.telefono, '3100000000')
        print("✅ Prueba 1 superada: El perfil del aprendiz se guarda correctamente en BD.")

    # 🟢 PRUEBA 2: Integridad de la Relación Usuario-Aprendiz
    def test_relacion_usuario_aprendiz(self):
        # Verificamos que el aprendiz esté conectado a la cuenta correcta
        self.assertEqual(self.aprendiz.usuario.first_name, 'Carlos')
        print("✅ Prueba 2 superada: El aprendiz está conectado a su cuenta de usuario.")

    # 🟢 PRUEBA 3: Integridad de la Relación Aprendiz-Ficha
    def test_relacion_aprendiz_ficha(self):
        # Comprobamos que el estudiante no quede "volando" sin ficha
        self.assertEqual(self.aprendiz.numero_ficha.numero, '2999999')
        print("✅ Prueba 3 superada: El aprendiz está correctamente matriculado en su ficha.")

    # 🟢 PRUEBA 4: Seguridad del Panel (Acceso Restringido)
    def test_acceso_perfil_aprendiz_anonimo(self):
        # Alguien intenta entrar al panel del aprendiz sin iniciar sesión
        response = self.client.get(reverse('aprendices:perfil_aprendiz'))
        # El sistema debe bloquearlo (Código 302 Redirección al login)
        self.assertEqual(response.status_code, 302)
        print("✅ Prueba 4 superada: El panel del aprendiz bloquea a usuarios anónimos.")

    # 🟢 PRUEBA 5: Acceso Correcto al Panel
    def test_acceso_perfil_aprendiz_autenticado(self):
        # El aprendiz inicia sesión correctamente
        self.client.login(username='100200300', password='Password123')
        # Intenta entrar a su panel
        response = self.client.get(reverse('aprendices:perfil_aprendiz'))
        # El sistema lo deja pasar (Código 200 OK)
        self.assertEqual(response.status_code, 200)
        print("✅ Prueba 5 superada: El aprendiz puede ver su propio panel sin problemas.")