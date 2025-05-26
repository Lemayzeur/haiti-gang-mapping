from django import forms
from .models import GangReport, ExtraArea
from django.utils.translation import gettext_lazy as _

class GangReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GangReportForm, self).__init__(*args, **kwargs)

        placeholders = {
            'gang_name': _('Baz Pilat, 400 Mawozo...'),
            'main_area': _('Delmas 32'),
            'extra_areas': _('Croix-des-Bouquets, Carrefour, etc.'),
            'activities': _('Kidnapping, extortion, drug trafficking...'),
            'description': _('Mention major attacks, negotiations, etc.'),
            'rival_gangs': _('G9, Baz Gran Ravin...'),
            'sources': _('Le Nouvelliste article, RHI report...'),
            'comments': _('Notes from interviews or observations.'),
        }

        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': placeholder
                })

        date_format = ['%d/%m/%Y']
        self.fields['start_date'].input_formats = date_format
        self.fields['end_date'].input_formats = date_format

    class Meta:
        model = GangReport
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'},
                format='%d/%m/%Y',
            ),
            'end_date': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'},
                format='%d/%m/%Y',
            ),
            'is_active': forms.RadioSelect(choices=[(True, _('Yes')), (False, _('No'))]),
        }



class ExtraAreaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        date_format = ['%d/%m/%Y']
        self.fields['date_taken'].input_formats = date_format
        self.fields['end_date'].input_formats = date_format

    class Meta:
        model = ExtraArea
        fields = ['name', 'date_taken', 'end_date']
        widgets = {
            'date_taken': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'},
                format='%d/%m/%Y',
            ),
            'end_date': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'},
                format='%d/%m/%Y',
            ),
        }

ExtraAreaFormSet = forms.inlineformset_factory(
    GangReport, ExtraArea,
    form=ExtraAreaForm,
    extra=1,
    can_delete=True
)