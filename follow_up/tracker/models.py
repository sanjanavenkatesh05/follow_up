from django.db import models    
import secrets
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib import admin


# 1. clinic
# 2. userProfile
# 3. FollowUpTracker
# 4. PublicViewLog
# 5. Ruleset: clinic_code and public_token generation functions, user can only see follow-ups from their clinic

# Create your models here.


def generate_clinic_code():
    return secrets.token_hex(4) #8 characters
def generate_public_token():
    return secrets.token_urlsafe(32) # 43 characters

class Clinic(models.Model):
    name = models.CharField(max_length=255)
    clinic_code = models.CharField(max_length=16, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.clinic_code:
            for _ in range(5):
                self.clinic_code = generate_clinic_code()
                try:
                    return super().save(*args, **kwargs)
                except IntegrityError:
                    continue
            raise RuntimeError("Failed to generate unique clinic_code")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="users"
    )

    def __str__(self):
        return f"{self.user.username} ({self.clinic.name})"

class FollowUp(models.Model):

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("done", "Done"),
    ]

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="followups"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_followups"
    )

    patient_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES
    )

    notes = models.TextField(blank=True, null=True)

    due_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    public_token = models.CharField(
        max_length=128,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.public_token:
            for _ in range(5):
                self.public_token = generate_public_token()
                try:
                    return super().save(*args, **kwargs)
                except IntegrityError:
                    continue
            raise RuntimeError("Failed to generate unique public_token")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_name} ({self.clinic.name})"

class PublicViewLog(models.Model):
    followup = models.ForeignKey(
        FollowUp,
        on_delete=models.CASCADE,
        related_name="view_logs"
    )

    viewed_at = models.DateTimeField(auto_now_add=True)

    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"View of {self.followup.id} at {self.viewed_at}"
    

def get_followups_for_user(user):
    clinic = user.userprofile.clinic
    return FollowUp.objects.filter(clinic=clinic)
