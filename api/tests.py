from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Activity


class ActivityCreateTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="demo", password="demo123")

    def test_create_activity(self):
        url = "/api/activities/"
        data = {
            "title": "Parcial QA",
            "type": "Examen",
            "course": "Testing",
            "due_date": "2026-03-20",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Activity.objects.count(), 1)
        activity = Activity.objects.first()
        self.assertIsNotNone(activity)
        assert activity is not None
        self.assertEqual(activity.title, "Parcial QA")
