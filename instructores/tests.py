from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from instructores.models import Instructor

class InstructoresTests(TestCase):
    
    def setUp(self):
        """Preparamos el perfil del instructor"""
        self.user_profe = User.objects.create_user(
            username='profe123',
            password='Password123',
            first_name='Martha',
            is_staff=True # Los instructores tienen permisos especiales
        )
        self.instructor = Instructor.objects.create(
            usuario=self.user_profe,
            telefono='3000000000'
            # Si pide telefono obligatorio, ponlo: telefono='3000000000'
        )

    # 🟢 PRUEBA 1: Creación de Instructor
    def test_creacion_instructor(self):
        profe_bd = Instructor.objects.get(telefono='3000000000') # Buscamos por teléfono
        self.assertEqual(profe_bd.usuario.first_name, 'Martha')
        print("✅ Prueba 1 superada: El perfil del instructor se crea correctamente.")

    # 🟢 PRUEBA 2: Permisos de Staff
    def test_relacion_usuario_instructor(self):
        # Validamos que el sistema sí le dio poderes de instructor (Staff)
        self.assertTrue(self.instructor.usuario.is_staff)
        print("✅ Prueba 2 superada: El instructor tiene permisos administrativos asignados.")

    # 🟢 PRUEBA 3: Acceso denegado a su panel
    def test_acceso_panel_instructor_anonimo(self):
        # Un intruso intenta ver el historial de bitácoras
        response = self.client.get(reverse('bitacoras:listar_bitacoras'))
        self.assertEqual(response.status_code, 302) # Redirección
        print("✅ Prueba 3 superada: Las vistas del instructor bloquean intrusos.")

    # 🟢 PRUEBA 4: Acceso exitoso a su panel
    def test_acceso_panel_instructor_autenticado(self):
        # El profe inicia sesión
        self.client.login(username='profe123', password='Password123')
        response = self.client.get(reverse('bitacoras:listar_bitacoras'))
        self.assertEqual(response.status_code, 200) # OK
        print("✅ Prueba 4 superada: El instructor accede a su historial sin problemas.")

    # 🟢 PRUEBA 5: Modificación de su teléfono
    def test_actualizacion_perfil_instructor(self):
        self.instructor.telefono = '3111111111' # Actualizamos el teléfono
        self.instructor.save()
        profe_actualizado = Instructor.objects.get(id=self.instructor.id)
        self.assertEqual(profe_actualizado.telefono, '3111111111')
        print("✅ Prueba 5 superada: El perfil del instructor se puede actualizar.")