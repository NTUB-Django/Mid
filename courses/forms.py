from django import forms

from .models import Department, EduType


class OfferingFilterForm(forms.Form):
    q = forms.CharField(label="關鍵字", required=False, max_length=80)
    edu = forms.ModelChoiceField(
        label="學制",
        required=False,
        queryset=EduType.objects.all(),
        empty_label="全部學制",
    )
    dept = forms.ModelChoiceField(
        label="系所",
        required=False,
        queryset=Department.objects.all(),
        empty_label="全部系所",
    )
