from django.test import Client, TestCase
from django.urls import reverse

# Create your tests here.
class CoreTests(TestCase):
    def test_register_and_login(self):
        resp = self.client.post(path=reverse("core:user_register"), data={"username": "RomanH3", "password": "posaune345", "email": "romanheus1999@gmail.com"})
        self.assertEqual(resp.status_code, 302)
        resp = self.client.post(path=reverse("core:request_login"), data={"username": "RomanH", "password": "posaune"})
        print(resp.get)
        self.assertEqual(resp.status_code, 400)
