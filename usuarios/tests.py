from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class UsuariosTestCase(TestCase):
    def setUp(self):
        # Esta función prepara el terreno ANTES de cada prueba
        # 1. Creamos un cliente web simulado (como un navegador invisible)
        self.client = Client()
        
        # 2. Creamos un usuario de prueba en la base de datos temporal
        self.usuario_prueba = User.objects.create_user(
            username='100200300', 
            password='PasswordSegura123',
            email='aprendiz@misena.edu.co',
            first_name='Juan',
            last_name='Pérez'
        )

    def test_login_exitoso(self):
        """Prueba que un usuario registrado pueda iniciar sesión correctamente"""
        
        # Simulamos que alguien llena el formulario de login y le da a "Entrar"
        response = self.client.post(reverse('usuarios:login'), {
            'username': '100200300',
            'password': 'PasswordSegura123'
        })
        
        # Verificamos que el sistema lo deje entrar y lo redirija (Código 302 es redirección exitosa)
        self.assertEqual(response.status_code, 302)
        
    def test_login_fallido_contrasena_incorrecta(self):
        """Prueba que el sistema rechace a un intruso con mala contraseña"""
        
        response = self.client.post(reverse('usuarios:login'), {
            'username': '100200300',
            'password': 'ClaveEquivocada'
        })
        
        # Al fallar, la página simplemente recarga mostrando un error (Código 200)
        self.assertEqual(response.status_code, 200)
        # Verificamos que se muestre el mensaje de error en el HTML
        self.assertContains(response, 'Por favor introduzca un nombre de usuario y clave correctos')