from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from .models import User, Activity, Subtask

class ProductivityTests(APITestCase):
    def setUp(self):
        # Crear Usuario A
        self.user_a = User.objects.create_user(
            username='user_a', 
            password='password123',
            email='a@example.com',
            daily_hour_limit=6.0
        )
        # Crear Usuario B
        self.user_b = User.objects.create_user(
            username='user_b', 
            password='password123',
            email='b@example.com'
        )
        
        # Obtener tokens
        response = self.client.post(reverse('login'), {'username': 'user_a', 'password': 'password123'})
        self.token_a = response.data['tokens']['access']
        
        response = self.client.post(reverse('login'), {'username': 'user_b', 'password': 'password123'})
        self.token_b = response.data['tokens']['access']

        # Datos de prueba para Usuario A
        self.today = timezone.now().date()
        
        # Actividad para Usuario A
        self.act_a = Activity.objects.create(
            user=self.user_a,
            title="Actividad A",
            type="estudio",
            course="Matematicas",
            work_date=timezone.now() + timedelta(days=5)
        )

    def set_auth_a(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_a)

    def set_auth_b(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_b)

    def test_today_grouping_and_ordering(self):
        """US-04: Test grouping (Overdue, Today, Coming Up) and tie-break by effort."""
        self.set_auth_a()
        
        # 1. Vencida (hace 2 días, 5h)
        Subtask.objects.create(activity=self.act_a, name="Vencida 1", target_date=self.today - timedelta(days=2), estimated_hours=5)
        # 2. Vencida (hace 1 día, 2h) - Debería ir después por fecha
        Subtask.objects.create(activity=self.act_a, name="Vencida 2", target_date=self.today - timedelta(days=1), estimated_hours=2)
        # 3. Hoy (3h)
        Subtask.objects.create(activity=self.act_a, name="Hoy 1", target_date=self.today, estimated_hours=3)
        # 4. Hoy (1h) - Debería ir primero en su grupo por menor esfuerzo
        Subtask.objects.create(activity=self.act_a, name="Hoy 2", target_date=self.today, estimated_hours=1)
        # 5. Próxima (mañana, 4h)
        Subtask.objects.create(activity=self.act_a, name="Prox 1", target_date=self.today + timedelta(days=1), estimated_hours=4)

        response = self.client.get(reverse('today'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        groups = response.data['groups']
        
        # Validar Vencidas (Orden por fecha ASC)
        self.assertEqual(groups['overdue']['tasks'][0]['name'], "Vencida 1")
        self.assertEqual(groups['overdue']['tasks'][1]['name'], "Vencida 2")
        
        # Validar Hoy (Tie-break por esfuerzo ASC)
        self.assertEqual(groups['today']['tasks'][0]['name'], "Hoy 2") # 1h < 3h
        self.assertEqual(groups['today']['tasks'][1]['name'], "Hoy 1")
        
        # Validar Próximas
        self.assertEqual(groups['coming_up']['tasks'][0]['name'], "Prox 1")

    def test_data_isolation_idor(self):
        """TS-04 / US-11: Usuario B no debe ver datos de Usuario A."""
        # Usuario A crea una subtarea
        Subtask.objects.create(activity=self.act_a, name="Privada A", target_date=self.today, estimated_hours=1)
        
        # Usuario B consulta "hoy"
        self.set_auth_b()
        response = self.client.get(reverse('today'))
        
        # Debería estar vacío para B
        self.assertEqual(response.data['total_count'], 0)
        self.assertEqual(len(response.data['groups']['today']['tasks']), 0)

    def test_profile_limit_validation(self):
        """US-12: Validar rango de 1-16 horas en el límite diario."""
        self.set_auth_a()
        url = reverse('update_profile')
        
        # Caso error: Demasiadas horas
        response = self.client.put(url, {'daily_hour_limit': 17.0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('daily_hour_limit', response.data)
        
        # Caso error: Muy pocas horas
        response = self.client.put(url, {'daily_hour_limit': 0.5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Caso éxito
        response = self.client.put(url, {'daily_hour_limit': 10.0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['daily_hour_limit']), 10.0)

    def test_today_filters(self):
        """US-05: Probar filtros por curso."""
        # Crear otra actividad con curso diferente
        act_fisica = Activity.objects.create(
            user=self.user_a, title="Fisica", type="estudio", course="Fisica", 
            work_date=timezone.now() + timedelta(days=5)
        )
        Subtask.objects.create(activity=self.act_a, name="Math Task", target_date=self.today, estimated_hours=1)
        Subtask.objects.create(activity=act_fisica, name="Fisica Task", target_date=self.today, estimated_hours=1)

        self.set_auth_a()
        
        # Sin filtro: 2 tareas
        response = self.client.get(reverse('today'))
        self.assertEqual(response.data['total_count'], 2)
        
        # Con filtro Math: 1 tarea
        response = self.client.get(reverse('today'), {'course': 'Matematicas'})
        self.assertEqual(response.data['total_count'], 1)
        self.assertEqual(response.data['groups']['today']['tasks'][0]['name'], "Math Task")
