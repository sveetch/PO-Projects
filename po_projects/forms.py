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
from crispy_forms.bootstrap import UneditableField
from crispy_forms_foundation.layout import Layout, Fieldset, Row, Column, ButtonHolder, Submit

from babel import Locale
from babel.core import UnknownLocaleError, get_locale_identifier
from babel.messages.pofile import read_po

from po_projects.models import Project, TemplateMsg, Catalog, TranslationMsg


class SourceTextField(UneditableField):
    """
    Layout object for rendering template field as simple html text
    """
    template = "po_projects/input_as_text.html"


class ProjectForm(forms.ModelForm):
    """Project Form"""
    po_file = forms.FileField(label=_('POT File'), required=True, help_text='Upload a valid POT file to initialize project strings to translate')
    
    def __init__(self, author=None, *args, **kwargs):
        self.uploaded_catalog = None
        self.catalog_entries = []
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Submit'))

        super(ProjectForm, self).__init__(*args, **kwargs)

    def clean_po_file(self):
        data = self.cleaned_data['po_file']
        if data:
            try:
                self.uploaded_catalog = read_po(data, ignore_obsolete=True)
            except:
                raise forms.ValidationError("Your file does not seem to be a valid POT file")

        return data

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.version = "0.1.0"
        
        if commit:
            project.header_comment = self.uploaded_catalog.header_comment
            project.mime_headers = json.dumps(dict(self.uploaded_catalog.mime_headers))
            project.save()
            
            entries = []
            for message in self.uploaded_catalog:
                if message.id:
                    flags = json.dumps(list(message.flags))
                    locations = json.dumps(message.locations)
                    entries.append(TemplateMsg(project=project, message=message.id, locations=locations, flags=flags))
                
            TemplateMsg.objects.bulk_create(entries)
            
        return project

    class Meta:
        model = Project
        exclude = ('version', 'header_comment', 'mime_headers')


class CatalogForm(forms.ModelForm):
    """Catalog base Form"""
    def __init__(self, project=None, *args, **kwargs):
        self.project = project
        self.fill_messages = not(kwargs.get('instance'))
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Submit'))

        super(CatalogForm, self).__init__(*args, **kwargs)

    def clean_locale(self):
        data = self.cleaned_data['locale']
        if data:
            # only accept "_" as separator, all "-" are replaced to "_"
            data = "_".join(data.split("-"))
            try:
                self.locale_trans = Locale.parse(data)
            except UnknownLocaleError:
                raise forms.ValidationError("Invalid locale")
            except ValueError:
                raise forms.ValidationError("Invalid locale")
            else:
                data = get_locale_identifier((self.locale_trans.language, self.locale_trans.territory, self.locale_trans.script, self.locale_trans.variant), sep='_')
        return data

    def save(self, commit=True):
        catalog = super(CatalogForm, self).save(commit=False)
        catalog.project = self.project
        
        if commit:
            catalog.header_comment = self.project.header_comment
            catalog.mime_headers = self.project.mime_headers
            catalog.save()
            
            # Only fill catalog with template messages on the first create
            if self.fill_messages:
                entries = []
                for row in self.project.templatemsg_set.all():
                    entries.append(TranslationMsg(template=row, catalog=catalog, message=''))
            
                TranslationMsg.objects.bulk_create(entries)
            
        return catalog

    class Meta:
        model = Catalog
        exclude = ('project', 'header_comment', 'mime_headers')


class CatalogUpdateForm(CatalogForm):
    """Catalog update Form"""
    po_file = forms.FileField(label=_('PO File'), required=False, help_text='Upload a valid PO file to update catalog messages, it will only update allready existing messages from the template, it does not add new message or remove existing messages. Be careful this will overwrite previous translations.')
    
    def __init__(self, project=None, *args, **kwargs):
        self.fill_messages = False # Never re-fill catalog with translation from template
        self.uploaded_catalog = None
        
        super(CatalogUpdateForm, self).__init__(project, *args, **kwargs)

    def clean_po_file(self):
        data = self.cleaned_data['po_file']
        if data:
            try:
                self.uploaded_catalog = read_po(data, ignore_obsolete=True)
            except:
                raise forms.ValidationError("Your file does not seem to be a valid PO file")

        return data

    def save(self, commit=True):
        catalog = super(CatalogUpdateForm, self).save(commit=commit)
        
        # Get all allready saved messages
        current_messages = dict([(item.template.message, item) for item in catalog.translationmsg_set.select_related('template').all()])
        
        if self.uploaded_catalog:
            uploaded_entries = []
            for message in self.uploaded_catalog:
                if message.id:
                    # Update message if allready exist in database and if different from the source
                    if message.id in current_messages and message.string != current_messages[message.id].message:
                        current_messages[message.id].message = message.string
                        current_messages[message.id].fuzzy = message.fuzzy
                        current_messages[message.id].pluralizable = message.pluralizable
                        current_messages[message.id].python_format = message.python_format
                        current_messages[message.id].save()
        
        return catalog


class TranslationMsgForm(forms.ModelForm):
    """Translation Form"""
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            Row(
                Column(
                    SourceTextField('template'),
                    css_class='small-6'
                ),
                Column(
                    'fuzzy',
                    'message',
                    css_class='small-6'
                ),
            ),
        )
        self.helper.add_input(Submit('submit', 'Submit'))

        super(TranslationMsgForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super(TranslationMsgForm, self).save(commit=False)
        
        if commit:
            message.save()
            
        return message

    class Meta:
        model = TranslationMsg
        exclude = ('catalog',)
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

