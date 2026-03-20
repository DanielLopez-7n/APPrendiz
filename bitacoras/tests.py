from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from aprendices.models import Aprendiz
from bitacoras.models import Bitacora
from fichas.models import Ficha        
from programas.models import Programa  
from datetime import date               

class BitacorasTests(TestCase):
    
    def setUp(self):
        """
        Preparación de los actores principales antes de cada prueba.
        (Efecto dominó: Programa -> Ficha -> Aprendiz)
        """
        # 1. Creamos al Instructor
        self.user_instructor = User.objects.create_user(
            username='987654321', password='Password123', email='profe@sena.edu.co', is_staff=True
        )

        # 2. Creamos un Programa falso
        self.programa = Programa.objects.create(
            nombre='Analisis y Desarrollo de Software'
            # (NOTA: Si en tu modelo Programa tienes un campo llamado 'codigo' que sea obligatorio,
            # agrégalo aquí, por ejemplo: codigo='228118' )
        )

        # 3. Creamos una Ficha falsa (con los campos exactos que me mostraste)
        self.ficha = Ficha.objects.create(
            numero='2999999', 
            programa=self.programa,
            fecha_inicio=date(2023, 1, 1),
            fecha_fin=date(2024, 12, 31)
        )

        # 4. Creamos al Aprendiz falso
        self.user_aprendiz = User.objects.create_user(
            username='123456789', password='Password123', email='estudiante@sena.edu.co'
        )
        self.aprendiz = Aprendiz.objects.create(
            usuario=self.user_aprendiz,
            documento='123456789',
            telefono='3001112233',
            numero_ficha=self.ficha 
        )
        
        
    # 🟢 PRUEBA 1: Estado por Defecto del Modelo
    def test_estado_inicial_bitacora(self):
        # Instanciamos una bitácora en memoria (sin guardarla aún)
        bitacora_nueva = Bitacora()
        # Verificamos que el sistema le asigne 'Pendiente' automáticamente
        self.assertEqual(bitacora_nueva.estado, 'Pendiente')
        print("✅ Prueba 1 superada: Las bitácoras nuevas nacen con estado 'Pendiente'.")

    # 🟢 PRUEBA 2: Seguridad y Protección de Rutas
    def test_acceso_denegado_crear_bitacora_anonimo(self):
        # Alguien intenta entrar directo a crear una bitácora sin iniciar sesión
        response = self.client.get(reverse('bitacoras:crear_bitacora'))
        # El sistema debe bloquearlo y mandarlo al login (302)
        self.assertEqual(response.status_code, 302)
        print("✅ Prueba 2 superada: El formulario de bitácoras está protegido.")

    # 🟢 PRUEBA 3: Acceso Permitido al Aprendiz
    def test_acceso_permitido_crear_bitacora_aprendiz(self):
        # El aprendiz inicia sesión
        self.client.login(username='123456789', password='Password123')
        # Intenta entrar al formulario
        response = self.client.get(reverse('bitacoras:crear_bitacora'))
        # El sistema le permite ver la página (200 OK)
        self.assertEqual(response.status_code, 200)
        print("✅ Prueba 3 superada: El aprendiz puede acceder a su formulario.")

    # 🟢 PRUEBA 4: API AJAX Exitosa (Auto-llenado del Instructor)
    def test_api_instructor_exitosa(self):
        self.client.login(username='123456789', password='Password123')
        
        # Simulamos la petición que hace JavaScript (Fetch) al backend
        url_api = reverse('bitacoras:obtener_datos_instructor', args=[self.user_instructor.id])
        response = self.client.get(url_api)
        
        # Verificamos que devuelva JSON y los datos correctos
        datos_json = response.json()
        self.assertTrue(datos_json['success'])
        self.assertEqual(datos_json['email'], 'profe@sena.edu.co')
        print("✅ Prueba 4 superada: La API devuelve los datos del instructor correctamente.")

    # 🟢 PRUEBA 5: API AJAX Manejo de Errores (Instructor inexistente)
    def test_api_instructor_fallida(self):
        self.client.login(username='123456789', password='Password123')
        
        # Simulamos pedir datos de un instructor que no existe (ID 9999)
        url_api = reverse('bitacoras:obtener_datos_instructor', args=[9999])
        response = self.client.get(url_api)
        
        datos_json = response.json()
        # El sistema no debe romperse, sino devolver un JSON con success = False
        self.assertFalse(datos_json['success'])
        self.assertIn('error', datos_json)
        print("✅ Prueba 5 superada: La API maneja correctamente los IDs inexistentes.")