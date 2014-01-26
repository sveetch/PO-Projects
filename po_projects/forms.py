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

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg


class SourceTextField(UneditableField):
    """
    Layout object for rendering template field as simple html text
    """
    template = "po_projects/input_as_text.html"


def create_templatemsgs(project_version, pot_catalog, commit=True):
    entries = []
    for message in pot_catalog:
        if message.id:
            #print message.id
            flags = json.dumps(list(message.flags))
            locations = json.dumps(message.locations)
            entries.append(TemplateMsg(project_version=project_version, message=message.id, locations=locations, flags=flags))
        
    if commit:
        TemplateMsg.objects.bulk_create(entries)
        
    return entries


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
        project.save()
        
        # Create a the first project_version
        self.create_new_version(project, 1)
            
        return project
    
    def create_new_version(self, project, version):
        """
        Open a new version for a project and fill it with datas from the given 
        POT file
        """
        project_version = project.projectversion_set.create(
            version = version,
            header_comment = self.uploaded_catalog.header_comment,
            mime_headers = json.dumps(dict(self.uploaded_catalog.mime_headers)),
        )
        create_templatemsgs(project_version, self.uploaded_catalog)
        
        return project_version

    class Meta:
        model = Project


class ProjectUpdateForm(ProjectForm):
    """Project Form for update"""
    def __init__(self, author=None, *args, **kwargs):
        super(ProjectUpdateForm, self).__init__(*args, **kwargs)
        
        self.fields['po_file'].required = False

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        
        if commit:
            if self.uploaded_catalog:
                previous_version = project.get_current_version()
                current_version = self.create_new_version(project, previous_version.version+1)
                self.update_catalogs(project, previous_version, current_version)
            project.save()
            
        return project

    def update_catalogs(self, project, previous_version, current_version):
        """
        Recreate all existing catalogs from previous version in the current one, 
        then update them from the given POT file
        """
        current_template = current_version.get_babel_template()
        current_templatemsg_map = dict([(item.message, item) for item in current_version.templatemsg_set.all()])
        
        # For each existing catalog in previous project version
        for previous_catalog in previous_version.catalog_set.all():
            # Update previous catalog from the given POT file
            current_babel_catalog = previous_catalog.get_babel_catalog()
            current_babel_catalog.update(current_template)
            
            # New catalog for current version
            current_catalog = current_version.catalog_set.create(
                locale = previous_catalog.locale,
                header_comment = current_version.header_comment,
                mime_headers = current_version.mime_headers,
            )
            
            # Add entries to the new catalog from template messages
            entries = []
            for template_id,template_instance in current_templatemsg_map.items():
                message = ''
                fuzzy = False
                if template_id in current_babel_catalog:
                    if current_babel_catalog[template_id].string:
                        message = current_babel_catalog[template_id].string
                    fuzzy = current_babel_catalog[template_id].fuzzy
                entries.append(TranslationMsg(template=template_instance, catalog=current_catalog, message=message, fuzzy=fuzzy))
            
            # Bulk saving entries
            TranslationMsg.objects.bulk_create(entries)


class CatalogForm(forms.ModelForm):
    """Catalog base Form"""
    def __init__(self, project_version=None, *args, **kwargs):
        self.project_version = project_version
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
    po_file = forms.FileField(label=_('PO File'), required=False, help_text='Upload a valid PO file to update catalog messages, it will only update allready existing messages from the template, it does not add new message or remove existing messages. Be careful this will overwrite previous translations.')
    
    def __init__(self, project_version=None, *args, **kwargs):
        self.fill_messages = False # Never re-fill catalog with translation from template
        self.uploaded_catalog = None
        
        super(CatalogUpdateForm, self).__init__(project_version, *args, **kwargs)

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

