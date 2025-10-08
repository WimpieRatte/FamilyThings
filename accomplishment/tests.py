from django.test import Client, TestCase
from django.urls import reverse


class AccomplishmentTests(TestCase):
    def test_bad_request_when_not_logged_in(self):
        url = reverse("accomplishment:get")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 400)

