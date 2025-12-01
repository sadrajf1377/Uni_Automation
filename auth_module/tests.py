from django.test import TestCase
from django.urls import reverse


# Create your tests here.
class Test_RateLimit(TestCase):
    def setUp(self):
        self.responses=[self.client.get(reverse('login')).status_code for x in range(7)]
    def test(self):
        print(self.responses)
