# Django
from django import forms

from .models import EmailSend, Event, MailingList


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "date", "time", "format", "description"]
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


class MailingListForm(forms.ModelForm):
    class Meta:
        model = MailingList
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class EmailSendForm(forms.ModelForm):
    class Meta:
        model = EmailSend
        fields = ["title", "mailing_list", "date", "time"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }


class ReceiptForm(forms.Form):
    username = forms.CharField(max_length=150, required=False)
    opens = forms.IntegerField(min_value=0, required=False)
    clicks = forms.IntegerField(min_value=0, required=False)
    receipt_id = forms.IntegerField(required=False)
    action = forms.CharField(max_length=20)
