from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.dispatch import receiver

DEPARTMENT_CHOICES = [
    ("Ouest", _("Ouest")),
    ("Artibonite", _("Artibonite")),
    ("Nord", _("Nord")),
    ("Centre", _("Centre")),
    ("Grande-Anse", _("Grande-Anse")),
    ("Nippes", _("Nippes")),
    ("Nord-Est", _("Nord-Est")),
    ("Nord-Ouest", _("Nord-Ouest")),
    ("Sud", _("Sud")),
    ("Sud-Est", _("Sud-Est")),
]

def generate_unique_slug(instance, slug_field='slug', base_field='gang_name'):
    base_slug = slugify(getattr(instance, base_field))
    slug = base_slug
    model = instance.__class__
    n = 1
    while model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{n}"
        n += 1
    return slug

class GangReport(models.Model):
    class Meta:
        db_table = 'gang_reports'


    created_at = models.DateTimeField(
        auto_now_add = True,
        verbose_name="Date Submitted"
    )

    modified_at = models.DateTimeField(
        auto_now = True,
        verbose_name="Last Modified"
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    gang_name = models.CharField(
        max_length=100,
        verbose_name=_('What is the name of the gang?'),
        help_text=_('If there’s no official name, write the name used locally.'),
    )
    is_active = models.BooleanField(
        verbose_name=_('Is this gang still active?'),
        help_text=_('Check "Yes" if the gang is currently operating.'),
    )
    start_date = models.DateField(
        null=True, blank=True,
        verbose_name=_('If known, when did this gang begin operating?'),
        help_text=_('Enter the approximate start date if known.'),
    )
    end_date = models.DateField(
        null=True, blank=True,
        verbose_name=_('If known, when did this gang stop operating?'),
        help_text=_('Leave blank if the gang is still active or the date is unknown.'),
    )
    main_area = models.CharField(
        max_length=255,
        verbose_name=_('Main neighborhood or area where this gang operates/operated?'),
        help_text=_('(e.g., Cité Soleil, Martissant, Delmas 32, etc.)'),
    )
    # extra_areas = models.TextField(
    #     blank=True,
    #     verbose_name=_('Additional places this gang controls or used to control (if any):'),
    #     help_text=_('Separate multiple areas with commas.'),
    # )
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        verbose_name=_('Which department does this location belong to?'),
        help_text=_('Select the department where the gang is/was most active.'),
    )
    activities = models.TextField(
        verbose_name=_('What kind of activities is/was the gang involved in?'),
        help_text=_('Be as specific as possible. (e.g., kidnappings, drug trafficking, extortion)'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Describe the activities or key events involving this gang.'),
        help_text=_('Optional. Add any context or background details.'),
    )
    rival_gangs = models.CharField(
        max_length=255, blank=True,
        verbose_name=_('Do you know of any rival gangs in the same area?'),
        help_text=_('List known rival gangs, if any.'),
    )
    sources = models.TextField(
        blank=True,
        verbose_name=_('Sources or references (if applicable):'),
        help_text=_('(e.g., news report, local knowledge, eyewitness account, etc.)'),
    )
    comments = models.TextField(
        blank=True,
        help_text=_('Any additional comments or observations?'),
    )

    is_validated = models.BooleanField(
        default=False,
        verbose_name=_('Validated for public display?'),
        help_text=_('Mark this report as validated before it appears on the website.'),
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edits',
        verbose_name=_('Parent report'),
        help_text=_('If this is an edit, link to the original report.'),
    )

    def __str__(self):
        return self.gang_name


class ExtraArea(models.Model):
    gang_report = models.ForeignKey('GangReport', related_name='extra_areas', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_('Area name'))
    date_taken = models.DateField(null=True, blank=True, verbose_name=_('Date taken by the gang'))
    end_date = models.DateField(
        null=True, blank=True,
        verbose_name=_('If known, when did this gang stop operating in this area?'),
        help_text=_('Leave blank if the gang is still active or the date is unknown.'),
    )
    notes = models.TextField(blank=True, verbose_name=_('Other relevant details about this area'))

    class Meta:
        verbose_name = _('Extra Area')
        verbose_name_plural = _('Extra Areas')

    def __str__(self):
        return self.name

@receiver(pre_save, sender=GangReport)
def add_slug_to_gang_report(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = generate_unique_slug(instance)