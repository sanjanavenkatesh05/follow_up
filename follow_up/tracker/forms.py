from django import forms
from .models import FollowUp

class FollowUpForm(forms.ModelForm): #modelform for creating a follow_up
    class Meta:
        model = FollowUp
        fields = ["patient_name", "phone", "language", "due_date", "notes"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        # Basic validation: check if it contains at least some digits
        if not any(char.isdigit() for char in phone):
             raise forms.ValidationError("Phone number must contain digits.")
        return phone
