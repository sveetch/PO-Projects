# -*- coding: utf-8 -*-
"""
Forms for po_projects
"""
import json

from django.conf import settings
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, UneditableField
from crispy_forms_foundation.layout import Layout, Fieldset, Row, Column, ButtonHolder, Submit

from babel import Locale
from babel.core import UnknownLocaleError, get_locale_identifier
from babel.messages.pofile import read_po

from .models import Project, RowSource, ProjectTranslation, RowTranslate

class ProjectForm(forms.ModelForm):
    """Project Form"""
    po_file = forms.FileField(label=_('PO File'), required=True, help_text='Upload a valid PO file to initialize project strings to translate')
    
    def __init__(self, author=None, *args, **kwargs):
        self.catalog = None
        self.catalog_entries = []
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Submit'))

        super(ProjectForm, self).__init__(*args, **kwargs)

    def clean_po_file(self):
        data = self.cleaned_data['po_file']
        if data:
            try:
                self.catalog = read_po(data, ignore_obsolete=True)
            except:
                raise forms.ValidationError("Your file does not seem to be a valid PO file")

        return data

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.version = "0.1.0"
        
        if commit:
            project.header_comment = self.catalog.header_comment
            project.mime_headers = json.dumps(dict(self.catalog.mime_headers))
            project.save()
            
            entries = []
            for message in self.catalog:
                if message.id:
                    flags = message.flags
                    if flags == set([]):
                        flags = ''
                    entries.append(RowSource(project=project, message=message.id, locations=json.dumps(message.locations), flags=flags))
                
            RowSource.objects.bulk_create(entries)
            
        return project

    class Meta:
        model = Project
        exclude = ('version', 'header_comment', 'mime_headers')

class ProjectTranslationForm(forms.ModelForm):
    """Catalog Form"""
    def __init__(self, project=None, *args, **kwargs):
        self.project = project
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Submit'))

        super(ProjectTranslationForm, self).__init__(*args, **kwargs)

    def clean_locale(self):
        data = self.cleaned_data['locale']
        if data:
            # only accept "_" as separator, all "-" are replaced to "_"
            data = "_".join(data.split("-"))
            try:
                self.locale_trans = Locale.parse(data)
            except UnknownLocaleError:
                raise forms.ValidationError("Invalid locale")
            else:
                data = get_locale_identifier((self.locale_trans.language, self.locale_trans.territory, self.locale_trans.script, self.locale_trans.variant), sep='_')
        return data

    def save(self, commit=True):
        trans = super(ProjectTranslationForm, self).save(commit=False)
        trans.project = self.project
        
        if commit:
            trans.header_comment = self.project.header_comment
            trans.mime_headers = self.project.mime_headers
            trans.save()
            
            entries = []
            for row in self.project.rowsource_set.all():
                entries.append(RowTranslate(source=row, translation=trans, message=''))
            
            RowTranslate.objects.bulk_create(entries)
            
        return trans

    class Meta:
        model = ProjectTranslation
        exclude = ('project', 'header_comment', 'mime_headers')

class SourceTextField(UneditableField):
    """
    Layout object for rendering source field as simple html text
    """
    template = "po_projects/translation_source_input.html"

class RowTranslationForm(forms.ModelForm):
    """Translation Form"""
    def __init__(self, translation=None, message=None, *args, **kwargs):
        self.translation = translation
        self.message = message
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            Fieldset(
                _('Your message'),
                Row(
                    Column(
                        SourceTextField('source'),
                        css_class='twelve'
                    ),
                ),
                Row(
                    Column(
                        'message',
                        css_class='twelve'
                    ),
                ),
            ),
        )
        self.helper.add_input(Submit('submit', 'Submit'))

        super(RowTranslationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super(RowTranslationForm, self).save(commit=False)
        message.source = self.message
        message.translation = self.translation
        
        if commit:
            message.save()
            
        return trans

    class Meta:
        model = RowTranslate
        exclude = ('translation',)

