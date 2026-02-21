# Django
from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "date", "time", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class AttendanceForm(forms.Form):
    username = forms.CharField(max_length=150, required=False)
    status = forms.CharField(max_length=20, required=False)
    attendance_id = forms.IntegerField(required=False)
    action = forms.CharField(max_length=20)
