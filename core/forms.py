from django import forms
from .models import GangReport, ExtraArea
from django.utils.translation import gettext_lazy as _

import datetime

    
MONTHS = [('', _('Month'))] + [
    (i, _(datetime.date(2000, i, 1).strftime('%B'))) for i in range(1, 13)
]

YEARS = [('', _('Year'))] + [
    (y, y) for y in range(datetime.date.today().year, 1999, -1)
]


ACTIVITY_CHOICES = [
    ('kidnapping', _('Kidnapping')),
    ('extortion', _('Extortion')),
    ('murder', _('Murder')),
    ('drug_trafficking', _('Drug trafficking')),
    ('robbery', _('Robbery')),
    ('rape', _('Rape')),
    ('human_trafficking', _('Human trafficking')),
    ('armed_assaults', _('Armed assaults')),
    ('carjacking', _('Carjacking')),
    ('illegal_arms_trade', _('Illegal arms trade')),
    ('smuggling', _('Smuggling')),
    ('other', _('Other')),
]


SOURCE_CHOICES = [
    ('social_media', _('Social Media')),
    ('mouth_to_mouth', _('Word of Mouth')),
    ('newspaper', _('Newspaper')),
    ('radio', _('Radio')),
    ('tv', _('TV')),
    ('government_reports', _('Government Reports')),
    ('ngo_reports', _('NGO & Human Rights Organizations')),
    ('community_watch', _('Community Watch Groups')),
    ('other', _('Other')),
]



class GangReportForm(forms.ModelForm):
    # Replace DateFields with custom dropdowns
    start_month = forms.ChoiceField(choices=MONTHS, label=_("Start Month"),required=False,)
    start_year = forms.ChoiceField(choices=YEARS, label=_("Start Year"),required=False,)
    end_month = forms.ChoiceField(choices=MONTHS, label=_("End Month"),required=False,)
    end_year = forms.ChoiceField(choices=YEARS, label=_("End Year"),required=False,)


    activities = forms.MultipleChoiceField(
        choices=ACTIVITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("Gang Activities")
    )
    other_activity = forms.CharField(
        required=False,
        label=_("If Other, specify"),
        widget=forms.TextInput(attrs={'placeholder': _('Other activity...')})
    )

    sources = forms.MultipleChoiceField(
        choices=SOURCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("Sources")
    )
    other_source = forms.CharField(
        required=False,
        label=_("If Other, specify"),
        widget=forms.TextInput(attrs={'placeholder': _('Other source...')})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'gang_name': _('Baz Pilat, 400 Mawozo...'),
            'main_area': _('Delmas 32'),
            # 'extra_areas': _('Croix-des-Bouquets, Carrefour, etc.'),
            'activities': _('Kidnapping, extortion, drug trafficking...'),
            # 'description': _('Mention major attacks, negotiations, etc.'),
            'rival_gangs': _('G9, Baz Gran Ravin...'),
            # 'sources': _('Le Nouvelliste article, RHI report...'),
            # 'comments': _('Notes from interviews or observations.'),
        }

        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': placeholder
                })

        if self.instance and self.instance.pk:
            if self.instance.start_date:
                self.initial['start_month'] = self.instance.start_date.month
                self.initial['start_year'] = self.instance.start_date.year
            if self.instance.end_date:
                self.initial['end_month'] = self.instance.end_date.month
                self.initial['end_year'] = self.instance.end_date.year

            # Prepopulate activities
            if self.instance.activities:
                activity_list = [a.strip() for a in self.instance.activities.split(',')]
                known_activities = [choice[0] for choice in ACTIVITY_CHOICES]
                matched = [a for a in activity_list if a in known_activities]
                custom = [a for a in activity_list if a not in known_activities]
                self.initial['activities'] = matched + (['other'] if custom else [])
                if custom:
                    self.initial['other_activity'] = ', '.join(custom)

            # Prepopulate sources
            if self.instance.sources:
                source_list = [s.strip() for s in self.instance.sources.split(',')]
                known_sources = [choice[0] for choice in SOURCE_CHOICES]
                matched = [s for s in source_list if s in known_sources]
                custom = [s for s in source_list if s not in known_sources]
                self.initial['sources'] = matched + (['other'] if custom else [])
                if custom:
                    self.initial['other_source'] = ', '.join(custom)

    class Meta:
        model = GangReport
        fields = [  # exclude real date fields from form
            'gang_name', 'main_area', 'activities',
            'description', 'rival_gangs', 'sources', 'comments', 'is_active',
            'start_date', 'end_date', 'department',
        ]
        widgets = {
            # 'start_date': forms.DateInput(
            #     attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'},
            #     format='%d/%m/%Y',
            # ),
            # 'end_date': forms.DateInput(
            #     attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'},
            #     format='%d/%m/%Y',
            # ),
            'is_active': forms.RadioSelect(choices=[(True, _('Yes')), (False, _('No'))]),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        start_month = cleaned_data.get('start_month')
        end_year = cleaned_data.get('end_year')
        end_month = cleaned_data.get('end_month')

        start_date = None
        end_date = None


        # Build start_date if both parts are present
        if start_year and start_month:
            try:
                start_date = datetime.date(int(start_year), int(start_month), 1)
                cleaned_data['start_date'] = start_date
            except ValueError:
                self.add_error('start_date', (_("Invalid start date.")))

        # Build end_date if both parts are present
        if end_year and end_month:
            try:
                end_date = datetime.date(int(end_year), int(end_month), 1)
                cleaned_data['end_date'] = end_date
            except ValueError:
                self.add_error('end_date', (_("Invalid end date.")))

        # If both are present, validate order
        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', (_("Start date must be before or equal to end date.")))


        # Activities
        activities = cleaned_data.get('activities', [])
        other_activity = cleaned_data.get('other_activity', '').strip()
        if 'other' in activities:
            activities.remove('other')
            if other_activity:
                activities += [x.strip() for x in other_activity.split(',') if x.strip()]
        cleaned_data['activities'] = ', '.join(activities)

        # Sources
        sources = cleaned_data.get('sources', [])
        other_source = cleaned_data.get('other_source', '').strip()
        if 'other' in sources:
            sources.remove('other')
            if other_source:
                sources += [x.strip() for x in other_source.split(',') if x.strip()]
        cleaned_data['sources'] = ', '.join(sources)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.start_date = self.cleaned_data['start_date']
        instance.end_date = self.cleaned_data['end_date']
        instance.activities = self.cleaned_data['activities']
        instance.sources = self.cleaned_data['sources']
        if commit:
            instance.save()
        return instance


class ExtraAreaForm(forms.ModelForm):
    date_taken_month = forms.ChoiceField(choices=MONTHS, label=_("Start Month"), required=False,)
    date_taken_year = forms.ChoiceField(choices=YEARS, label=_("Start Year"), required=False,)
    end_date_month = forms.ChoiceField(choices=MONTHS, label=_("End Month"), required=False,)
    end_date_year = forms.ChoiceField(choices=YEARS, label=_("End Year"), required=False,)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            if self.instance.date_taken:
                self.initial['date_taken_month'] = self.instance.date_taken.month
                self.initial['date_taken_year'] = self.instance.date_taken.year
            if self.instance.end_date:
                self.initial['end_date_month'] = self.instance.end_date.month
                self.initial['end_date_year'] = self.instance.end_date.year

    class Meta:
        model = ExtraArea
        fields = ['name', 'date_taken', 'end_date']
        # widgets = {
        #     'date_taken': forms.DateInput(
        #         attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'},
        #         format='%d/%m/%Y',
        #     ),
        #     'end_date': forms.DateInput(
        #         attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'},
        #         format='%d/%m/%Y',
        #     ),
        # }

    def clean(self):
        cleaned_data = super().clean()

        date_taken_year = cleaned_data.get('date_taken_year')
        date_taken_month = cleaned_data.get('date_taken_month')
        end_date_year = cleaned_data.get('end_date_year')
        end_date_month = cleaned_data.get('end_date_month')

        date_taken = None
        end_date = None

        # Build date_taken if both parts are present
        if date_taken_year and date_taken_month:
            try:
                date_taken = datetime.date(int(date_taken_year), int(date_taken_month), 1)
                cleaned_data['date_taken'] = date_taken
            except ValueError:
                self.add_error('date_taken', _("Invalid start date."))

        # Build end_date if both parts are present
        if end_date_year and end_date_month:
            try:
                end_date = datetime.date(int(end_date_year), int(end_date_month), 1)
                cleaned_data['end_date'] = end_date
            except ValueError:
                self.add_error('end_date', _("Invalid end date."))

        # If both are present, validate order
        if date_taken and end_date and date_taken > end_date:
            self.add_error('end_date', _("Start date must be before or equal to end date."))

        return cleaned_data



    def save(self, commit=True):
        instance = super().save(commit=False)
        cleaned_data = self.cleaned_data
        instance.date_taken = cleaned_data.get('date_taken')
        instance.end_date = cleaned_data.get('end_date')
        if commit:
            instance.save()
        return instance

ExtraAreaFormSet = forms.inlineformset_factory(
    GangReport, ExtraArea,
    form=ExtraAreaForm,
    extra=1,
    can_delete=True
)