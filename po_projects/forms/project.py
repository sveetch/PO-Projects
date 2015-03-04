# -*- coding: utf-8 -*-
"""
Forms for po_projects projects
"""
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _

from babel.messages.pofile import read_po

from po_projects.models import Project
from po_projects.forms import CrispyFormMixin

from po_projects.generators import create_new_version, update_catalogs

class ProjectForm(CrispyFormMixin, forms.ModelForm):
    """Project Form"""
    crispy_form_helper_path = 'po_projects.forms.crispies.project_helper'
    
    po_file = forms.FileField(label=_('POT File'), required=True, help_text=_('Upload a valid POT file to initialize or update project strings to translate'))
    
    def __init__(self, author=None, *args, **kwargs):
        self.author = author
        self.uploaded_catalog = None
        self.catalog_entries = []
        
        self.crispy_form_helper_kwargs.update({
            'instance': kwargs.get('instance', None),
        })
        
        super(ProjectForm, self).__init__(*args, **kwargs)
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    def clean_po_file(self):
        data = self.cleaned_data['po_file']
        if data:
            try:
                self.uploaded_catalog = read_po(data, ignore_obsolete=True)
            except:
                raise forms.ValidationError(_("Your file does not seem to be a valid POT file"))

        return data

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        project.save()
        
        # Create a the first project_version
        create_new_version(project, 1, self.uploaded_catalog)
            
        return project

    class Meta:
        model = Project


class ProjectUpdateForm(ProjectForm):
    """Project Form for update"""
    def __init__(self, author=None, *args, **kwargs):
        super(ProjectUpdateForm, self).__init__(author, *args, **kwargs)
        
        self.fields['po_file'].required = False

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        
        if commit:
            if self.uploaded_catalog:
                previous_version = project.get_current_version()
                current_version = create_new_version(project, previous_version.version+1, self.uploaded_catalog)
                update_catalogs(project, previous_version, current_version)
            project.save()
            
        return project

    class Meta:
        model = Project
        exclude = ('slug',)
