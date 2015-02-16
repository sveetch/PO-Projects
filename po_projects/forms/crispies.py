# -*- coding: utf-8 -*-
"""
Crispy forms layouts
"""
import re

from django import forms
from django.utils.translation import ugettext as _

from django.utils.text import normalize_newlines
from django.utils.html import escape

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import UneditableField
from crispy_forms_foundation.layout import TEMPLATE_PACK, Layout, Row, Column, HTML, Div, Field, ButtonHolder, ButtonHolderPanel, ButtonGroup, Panel, Submit

def SimpleRowColumn(field, *args, **kwargs):
    """
    Shortcut for simple row with only a full column
    """
    if isinstance(field, basestring):
        field = Field(field, *args, **kwargs)
    return Row(
        Column(field),
    )

class SourceTextField(UneditableField):
    """
    Layout object for rendering template field value as html and a hidden input
    
    Field value rendering is at your charge in the template (default is to use 
    Django's 'linebreaks' filter)
    """
    template = "po_projects/input_as_text.html"
    
    def linebreaks(self, value, autoescape=True):
        """
        Converts newlines into <p> and <br />s. Additionnaly add a carriage return 
        character before each simple line break.
        
        Taken from ``django.utils.html.linebreaks`` then modified to fit needs.
        """
        value = normalize_newlines(value)
        paras = re.split('\n{2,}', value)
        if autoescape:
            paras = ['<p>%s</p>' % escape(p).replace('\n', u'<span class="explicit_cr">↵</span><br />') for p in paras]
        else:
            paras = ['<p>%s</p>' % p.replace('\n', u'<span class="explicit_cr">↵</span><br />') for p in paras]
        return '\n\n'.join(paras)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        context['source_content'] = self.linebreaks(form.instance.template.message)

        return super(SourceTextField, self).render(form, form_style, context, template_pack=TEMPLATE_PACK)

def translation_helper(instance=None, prefix='', form_tag=False):
    """
    Catalog's message translations form layout helper
    """
    helper = FormHelper()
    helper.form_action = '.'
    helper.form_class = 'catalog-messages-form'
    helper.form_tag = form_tag
    helper.disable_csrf = True
    helper.render_required_fields = True
    
    row_css_classes = ['message-row', 'clearfix']
    if instance is not None and instance.fuzzy:
        row_css_classes.append('fuzzy')
    elif instance is not None and not instance.message:
        row_css_classes.append('disabled empty')
    else:
        row_css_classes.append('enabled')
        
    anchor_link = ''
    if prefix:
        prefix_id = int(prefix[len('form-'):]) + 1
        anchor_link = '<a href="#item-{0}" id="item-{0}">#{0}</a>'.format(prefix_id)
    
    helper.layout = Layout(
        Div(
            Div(
                HTML(anchor_link),
                css_class='anchor',
            ),
            Div(
                Div(
                    'fuzzy',
                    css_class='fuzzy-field',
                ),
                Div(
                    Div(
                        SourceTextField('template'),
                        css_class='flex-item source',
                    ),
                    Field(
                        'message',
                        placeholder=_("Type your translation here else the original text will be used"),
                        wrapper_class='flex-item edit',
                    ),
                    css_class='flex-container',
                ),
                css_class=' '.join(row_css_classes),
            ),
            css_class='row-wrapper',
        ),
    )
    #helper.add_input(Submit('submit', 'Submit'))
    
    return helper
