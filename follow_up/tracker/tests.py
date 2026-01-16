from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Clinic, UserProfile, FollowUp, PublicViewLog
from django.urls import reverse
from datetime import date, timedelta

class FollowUpTrackerTests(TestCase):
    def setUp(self):
        # Create Clinic 1 & User 1
        self.clinic1 = Clinic.objects.create(name="Clinic One")
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.profile1 = UserProfile.objects.create(user=self.user1, clinic=self.clinic1)

        # Create Clinic 2 & User 2
        self.clinic2 = Clinic.objects.create(name="Clinic Two")
        self.user2 = User.objects.create_user(username="user2", password="password")
        self.profile2 = UserProfile.objects.create(user=self.user2, clinic=self.clinic2)

        # Create FollowUp for Clinic 1
        self.followup1 = FollowUp.objects.create(
            clinic=self.clinic1,
            created_by=self.user1,
            patient_name="Patient One",
            phone="1234567890",
            language="en",
            due_date=date.today() + timedelta(days=5),
            status="pending"
        )

        self.client = Client()

    def test_clinic_code_generation(self):
        """Test that clinic_code is generated and is unique."""
        self.assertTrue(self.clinic1.clinic_code)
        self.assertNotEqual(self.clinic1.clinic_code, self.clinic2.clinic_code)
        
        # Ensure length is correct (4 bytes hex = 8 chars)
        self.assertEqual(len(self.clinic1.clinic_code), 8)

    def test_public_token_generation(self):
        """Test that public_token is generated and is unique."""
        self.assertTrue(self.followup1.public_token)
        
        followup2 = FollowUp.objects.create(
            clinic=self.clinic1,
            created_by=self.user1,
            patient_name="Patient Two",
            phone="0987654321",
            language="hi",
            due_date=date.today(),
            status="pending"
        )
        self.assertNotEqual(self.followup1.public_token, followup2.public_token)

    def test_dashboard_requires_login(self):
        """Test that the dashboard requires login."""
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302) # Redirects to login

        self.client.login(username="user1", password="password")
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_cross_clinic_access_denied(self):
        """Test that a user cannot access/edit a followup from another clinic."""
        self.client.login(username="user2", password="password") # User from Clinic 2
        
        # Try to edit Clinic 1's followup
        response = self.client.get(reverse('edit_followup', args=[self.followup1.id]))
        
        # Should be Forbidden (403) or Not Found (404) depending on implementation
        # Our implementation returns 403 HttpResponseForbidden
        self.assertEqual(response.status_code, 403)

    def test_public_page_logging(self):
        """Test that accessing the public page creates a PublicViewLog entry."""
        initial_count = PublicViewLog.objects.count()
        
        url = reverse('public_followup', args=[self.followup1.public_token])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PublicViewLog.objects.count(), initial_count + 1)
        
        log = PublicViewLog.objects.last()
        self.assertEqual(log.followup, self.followup1)
