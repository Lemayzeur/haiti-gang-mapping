from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    # print('va', value)
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': css_class})
    # return value.as_widget(attrs={'class': css_class})
    # field = mark_safe()
    # return field.as_widget(attrs={**field.field.widget.attrs, 'class': css_class})
