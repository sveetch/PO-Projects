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
    Given a Babel Catalog return his PO export as a plain string
    """
    fpw = StringIO.StringIO()
    write_po(fpw, catalog, sort_by_file=False, ignore_obsolete=True, include_previous=False)
    content = fpw.getvalue()
    fpw.close()
    
    return content

class ProjectForm(forms.ModelForm):
    """Project Form"""
    pot_file = forms.FileField(label=_('POT File'), required=True, help_text='Upload a valid POT file to initialize project catalogs')
    
    def __init__(self, author=None, *args, **kwargs):
        self.author = author
        self.catalog = None
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Submit'))

        super(ProjectForm, self).__init__(*args, **kwargs)

    def clean_pot_file(self):
        data = self.cleaned_data['pot_file']
        if data:
            try:
                self.catalog = read_po(data, ignore_obsolete=True)
            except:
                raise forms.ValidationError("Your file does not seem to be a valid POT file")

        return data

    def get_version(self):
        return "0.1.0"

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.author = self.author
        #self.catalog.version = project.version = self.get_version()
        project.version = self.catalog.version
        #
        project.content = catalog_as_string(self.catalog)
        
        if commit:
            project.save()
            
        return project

    class Meta:
        model = Project
        exclude = ('version', 'author', 'content')

class ProjectUpdateForm(forms.ModelForm):
    """Project update Form"""
    pot_file = forms.FileField(label=_('POT File'), required=True, help_text='Upload a valid POT file to update all catalogs')
    
    def __init__(self, author=None, *args, **kwargs):
        self.author = author
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Submit'))

        super(ProjectUpdateForm, self).__init__(*args, **kwargs)

    def clean_pot_file(self):
        data = self.cleaned_data['pot_file']
        if data:
            try:
                self.catalog = read_po(data, ignore_obsolete=True)
            except:
                raise forms.ValidationError("Your file does not seem to be a valid POT file")

        return data

    def save(self, commit=True):
        project = super(ProjectUpdateForm, self).save(commit=False)
        project.content = catalog_as_string(self.catalog)
        
        if commit:
            project.save()
            
            update_project_catalogs(project, project.get_babel_catalog(force=True))
            
        return project

def update_project_catalogs(project, template_catalog, commit=True):
    """
    Update all project catalogs from his template catalog
    """
    for catalog in project.catalog_set.all().order_by('id'):
        babel_catalog = catalog.get_babel_catalog()
        babel_catalog.update(template_catalog)
        
        catalog.content = catalog_as_string(babel_catalog)
        if commit:
            catalog.save()
        
    return 
        
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
    _message_fuzzy_fieldname = 'msg_fuzzy_{0}'
    _message_text_fieldname = 'msg_string_{0}'
    
    def __init__(self, project=None, author=None, *args, **kwargs):
        self.project = project
        self.author = author
        self.catalog = kwargs.pop('instance')

        super(CatalogMessagesForm, self).__init__(*args, **kwargs)
        
        # Add each catalog message as a field group (checkbox+textarea) with its layout
        messages_layout = []
        for i, msg in enumerate(self.catalog.get_messages()):
            self.fields[self._message_fuzzy_fieldname.format(i)] = forms.BooleanField(label="fuzzy", required=False)
            self.fields[self._message_text_fieldname.format(i)] = forms.CharField(label=msg.id, widget=forms.Textarea(attrs={'rows':'3'}), required=False)
            messages_layout.append(Row(
                Column(
                    self._message_fuzzy_fieldname.format(i),
                    css_class='one'
                ),
                Column(
                    self._message_text_fieldname.format(i),
                    css_class='eleven'
                ),
            ))
        messages_layout.append(Row(
            Column(
                ButtonHolder(
                    Submit('submit', _('Send')),
                    css_class="text-right"
                ),
                css_class='twelve'
            ),
        ))
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.layout = Layout(*messages_layout)
    
    def clean(self):
        cleaned_data = super(CatalogMessagesForm, self).clean()
        
        for i, msg in enumerate(self.catalog.get_messages()):
            field_id = self._message_text_fieldname.format(i)
            # TODO: find errors to test the exception and catch it rightly
            #try:
            BabelMessage(msg.id, string=cleaned_data[field_id], locations=msg.locations, flags=msg.flags).check(self.catalog.get_babel_catalog())
            #except ???:
                #self._errors[field_id] = self.error_class(["Unvalid message"])
                #del cleaned_data[field_id]
        
        return cleaned_data
        
    def save(self, commit=True):
        if commit:
            babel_catalog = self.catalog.get_babel_catalog()
            # From each given field, fill the catalog rows
            for i, msg in enumerate(self.catalog.get_messages()):
                # Update the string from the textarea
                string_field_id = self._message_text_fieldname.format(i)
                babel_catalog[msg.id].string = self.cleaned_data[string_field_id]
                
                # Update the fuzzy flag from the checkbox value
                fuzzy_field_id = self._message_fuzzy_fieldname.format(i)
                flags = list(babel_catalog[msg.id].flags)
                if self.cleaned_data[fuzzy_field_id] and 'fuzzy' not in flags:
                    flags.append('fuzzy')
                elif not self.cleaned_data[fuzzy_field_id] and 'fuzzy' in flags:
                    flags = [f for f in flags if f!='fuzzy']
                
                babel_catalog[msg.id].flags = flags
            
            self.catalog.content = catalog_as_string(babel_catalog)
            
            self.catalog.save()
        
        return self.catalog
