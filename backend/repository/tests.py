from django.test import TestCase, Client


from django.contrib.auth.models import User

from .models import Dataset, Submission

class TestSubmissionCreate(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_get(self):
        reponse = self.client.get('/v2/submit/')
        self.assertEqual(reponse.status_code, 405)  # 405 Method Not Allowed
        
    def test_post(self):
        reponse = self.client.post('/v2/submit/')
        self.assertEqual(reponse.status_code, 401)  # 401 Unauthorized
        
        # Post with invalid token
        reponse = self.client.post('/v2/submit/', {"Authorization": "Bearer 123"})
        self.assertEqual(reponse.status_code, 401)  # 401 Unauthorized
        
        # Create user
        user = User.objects.create(username="test")
        
        # Create dataset
        dataset = Dataset.objects.create(name="Test", description="Test", created_by=User.objects.create(username="test"))
    