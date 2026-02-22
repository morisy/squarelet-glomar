# Django
from django import forms

from .models import EmailSend, Event, MailingList, ResearchContract, ResearchProject


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


class ResearchContractForm(forms.ModelForm):
    class Meta:
        model = ResearchContract
        fields = [
            "title",
            "organization",
            "total_hours",
            "start_date",
            "end_date",
            "status",
            "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "total_hours": forms.NumberInput(attrs={"step": "0.25"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = ["title", "size", "allotted_hours", "status", "description"]
        widgets = {
            "allotted_hours": forms.NumberInput(attrs={"step": "0.25"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class WorkLogForm(forms.Form):
    username = forms.CharField(max_length=150, required=False)
    hours = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    description = forms.CharField(required=False)
    work_date = forms.DateField(required=False)
    work_log_id = forms.IntegerField(required=False)
    action = forms.CharField(max_length=20)
