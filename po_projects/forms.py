# -*- coding: utf-8 -*-
"""
Forms for po_projects
"""
import json, StringIO

from django.conf import settings
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, UneditableField
from crispy_forms_foundation.layout import Layout, Fieldset, Row, Column, ButtonHolder, Submit

from babel import Locale
from babel.core import UnknownLocaleError, get_locale_identifier
from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Message as BabelMessage

from .models import Project, Catalog

def catalog_as_string(catalog):
    """
    Given a Babel Catalog return his PO export as a string
    """
    fpw = StringIO.StringIO()
    write_po(fpw, catalog, sort_by_file=False, ignore_obsolete=True, include_previous=False)
    content = fpw.getvalue()
    fpw.close()
    
    return content

class ProjectForm(forms.ModelForm):
    """Project Form"""
    po_file = forms.FileField(label=_('PO File'), required=True, help_text='Upload a valid PO file to initialize project strings to translate')
    
    def __init__(self, author=None, *args, **kwargs):
        self.author = author
        self.catalog = None
        
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

    def get_version(self):
        return "0.1.0"

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.author = self.author
        self.catalog.version = project.version = self.get_version()
        #
        project.content = catalog_as_string(self.catalog)
        
        if commit:
            project.save()
            
        return project

    class Meta:
        model = Project
        exclude = ('version', 'author', 'content')
        
class CatalogForm(forms.ModelForm):
    """Catalog Form"""
    def __init__(self, author=None, project=None, *args, **kwargs):
        self.author = author
        self.project = project
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Submit'))

        super(CatalogForm, self).__init__(*args, **kwargs)

    def clean_locale(self):
        """
        Try to parse the given locale identifier, if success return the full 
        identifier (as a string) finded by the babel locale parser
        """
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
        catalog = super(CatalogForm, self).save(commit=False)
        catalog.project = self.project
        catalog.author = self.author
        # Get the template catalog from project then fill it with meta datas from the catalog
        template_catalog = self.project.get_babel_catalog()
        template_catalog.last_translator = "{full_name} <{email}>".format(full_name=self.author.get_full_name(), email=self.author.email)
        template_catalog.locale = catalog.get_babel_locale()
        #template_catalog.revision_date = foo
        
        catalog.content = catalog_as_string(template_catalog)
        
        if commit:
            catalog.save()
            
        return catalog

    class Meta:
        model = Catalog
        exclude = ('project', 'author', 'content')

class CatalogMessagesForm(forms.Form):
    """Catalog messages Form"""
    def __init__(self, project=None, author=None, *args, **kwargs):
        self.project = project
        self.author = author
        self.catalog = kwargs.pop('instance')

        super(CatalogMessagesForm, self).__init__(*args, **kwargs)
        
        for i, msg in enumerate(self.catalog.get_messages()):
            self.fields['msg_{0}'.format(i)] = forms.CharField(label=msg.id, widget=forms.Textarea(attrs={'rows':'3'}), required=False)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Submit'))
    
    def clean(self):
        cleaned_data = super(CatalogMessagesForm, self).clean()
        
        for i, msg in enumerate(self.catalog.get_messages()):
            field_id = 'msg_{0}'.format(i)
            #try:
            BabelMessage(msg.id, string=cleaned_data[field_id], locations=msg.locations, flags=msg.flags).check(self.catalog.get_babel_catalog())
            #except ???:
                #self._errors[field_id] = self.error_class(["Unvalid message"])
                #del cleaned_data[field_id]
        
        return cleaned_data
        
    def save(self, commit=True):
        if commit:
            babel_catalog = self.catalog.get_babel_catalog()
            for i, msg in enumerate(self.catalog.get_messages()):
                field_id = 'msg_{0}'.format(i)
                babel_catalog[msg.id].string = self.cleaned_data[field_id]
            
            self.catalog.content = catalog_as_string(babel_catalog)
            
            self.catalog.save()
        
        return self.catalog
