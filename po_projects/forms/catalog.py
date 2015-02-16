# -*- coding: utf-8 -*-
"""
Forms for po_projects catalogs
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

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg
from po_projects.forms import CrispyFormMixin

from po_projects.utils import create_templatemsgs, create_new_version, update_catalogs

class CatalogForm(CrispyFormMixin, forms.ModelForm):
    """Catalog base Form"""
    crispy_form_helper_path = 'po_projects.forms.crispies.inline_catalog_helper'
    
    def __init__(self, author=None, project_version=None, *args, **kwargs):
        self.author = author
        self.project_version = project_version
        self.fill_messages = not(kwargs.get('instance'))

        super(CatalogForm, self).__init__(*args, **kwargs)
        super(forms.ModelForm, self).__init__(*args, **kwargs)

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

    def clean(self):
        cleaned_data = super(CatalogForm, self).clean()
        
        if not self.author.has_perm('po_projects.add_catalog'):
            raise forms.ValidationError(_("You don't have permission to use this form"))

        # Always return the full collection of cleaned data.
        return cleaned_data
    
    def save(self, commit=True):
        catalog = super(CatalogForm, self).save(commit=False)
        catalog.project_version = self.project_version
        
        if commit:
            catalog.header_comment = self.project_version.header_comment
            catalog.mime_headers = self.project_version.mime_headers
            catalog.save()
            
            # Only fill catalog with template messages on the first create
            if self.fill_messages:
                entries = []
                for row in self.project_version.templatemsg_set.all():
                    entries.append(TranslationMsg(template=row, catalog=catalog, message=''))
            
                TranslationMsg.objects.bulk_create(entries)
            
        return catalog

    class Meta:
        model = Catalog
        exclude = ('project_version', 'header_comment', 'mime_headers')


class CatalogUpdateForm(CatalogForm):
    """Catalog update Form"""
    crispy_form_helper_path = None
    
    po_file = forms.FileField(label=_('PO File'), required=False, help_text='Upload a valid PO file to update catalog messages, it will only update allready existing messages from the template, it does not add new message or remove existing messages. Be careful this will overwrite previous translations.')
    
    def __init__(self, author=None, project_version=None, *args, **kwargs):
        self.author = author
        self.fill_messages = False # Never re-fill catalog with translation from template
        self.uploaded_catalog = None
        
        super(CatalogUpdateForm, self).__init__(author, project_version, *args, **kwargs)

    def clean(self):
        cleaned_data = super(CatalogForm, self).clean()
        
        if not self.author.has_perm('po_projects.change_catalog'):
            raise forms.ValidationError(_("You don't have permission to use this form"))

        # Always return the full collection of cleaned data.
        return cleaned_data

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
        
        # Get all existing saved messages
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
