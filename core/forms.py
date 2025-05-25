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
    class Meta:
        model = GangReport
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'MM/DD/YYYY'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'MM/DD/YYYY'}),
            'is_active': forms.RadioSelect(choices=[(True, _('Yes')), (False, _('No'))]),
        }



class ExtraAreaForm(forms.ModelForm):
    class Meta:
        model = ExtraArea
        fields = ['name', 'date_taken', 'end_date']
        widgets = {
            'date_taken': forms.DateInput(attrs={'type': 'date', 'placeholder': 'MM/DD/YYYY'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'MM/DD/YYYY'}),
        }

ExtraAreaFormSet = forms.inlineformset_factory(
    GangReport, ExtraArea,
    form=ExtraAreaForm,
    extra=1,
    can_delete=True
)