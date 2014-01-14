# -*- coding: utf-8 -*-
"""
Page document views
"""
import json, os, StringIO

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django.forms.models import modelformset_factory

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog as BabelCatalog

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg
from po_projects.forms import ProjectForm, CatalogUpdateForm, TranslationMsgForm
from po_projects.utils import DownloadMixin


class CatalogDetails(LoginRequiredMixin, generic.UpdateView):
    """
    Form view to display Catalog details and edit its infos
    """
    model = Catalog
    template_name = "po_projects/catalog_details.html"
    form_class = CatalogUpdateForm

    def get(self, request, *args, **kwargs):
        self.project = self.get_project()
        self.project_version = self.get_project_version()
        return super(CatalogDetails, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project()
        self.project_version = self.get_project_version()
        return super(CatalogDetails, self).post(request, *args, **kwargs)

    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.project, version=self.kwargs['version'])
        return self.project.get_current_version()

    def get_object(self):
        return get_object_or_404(Catalog, project_version=self.project_version, locale=self.kwargs['locale'])
        
    def get_context_data(self, **kwargs):
        context = super(CatalogDetails, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'project_version': self.project_version,
            'catalog': self.object,
        })
        return context

    def get_success_url(self):
        return reverse('po_projects:catalog-details', args=[self.project.slug, self.object.locale])

    def get_form_kwargs(self):
        kwargs = super(CatalogDetails, self).get_form_kwargs()
        kwargs.update({
            'project_version': self.project_version,
        })
        return kwargs


def CatalogMessagesFormView(request, slug=None, version=None, locale=None):
    """
    Form view to edit messages from a catalog
    
    Implemented without CBV until i find HOW to do it with formset usage
    """
    template_name = "po_projects/catalog_messages_form.html"
    
    project = get_object_or_404(Project, slug=slug)
    if version is not None:
        project_version = get_object_or_404(ProjectVersion, project=project, version=version)
    else:
        project_version = project.get_current_version()
    catalog = get_object_or_404(Catalog, project_version=project_version, locale=locale)
    
    formset_queryset = TranslationMsg.objects.select_related('template').filter(catalog=catalog)
    
    TranslationMsgFormSet = modelformset_factory(TranslationMsg, form=TranslationMsgForm, fields=('template','fuzzy','message',), extra=0)
    
    formset = TranslationMsgFormSet(request.POST or None, queryset=formset_queryset)
    
    if formset.is_valid():
        formset.save()
    
    extra_context = {
        "project": project,
        "project_version": project_version,
        "catalog": catalog,
        "formset": formset
    }
    return render_to_response(template_name, extra_context, context_instance=RequestContext(request))


class CatalogMessagesExportView(LoginRequiredMixin, DownloadMixin, generic.View):
    """
    View to export PO file from a catalog
    """
    content_type = 'text/x-gettext-translation'
    filename_format = "messages_{locale_name}_{timestamp}.po"

    def get(self, request, *args, **kwargs):
        self.project = self.get_project()
        self.project_version = self.get_project_version()
        self.object = self.get_object()
        return super(CatalogMessagesExportView, self).get(request, *args, **kwargs)
    
    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.project, version=self.kwargs['version'])
        return self.project.get_current_version()

    def get_object(self):
        return get_object_or_404(Catalog, project_version=self.project_version, locale=self.kwargs['locale'])
        
    def get_context_data(self, **kwargs):
        context = super(CatalogMessagesExportView, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'project_version': self.project_version,
            'catalog': self.object,
            'locale_name': self.object.locale,
            'timestamp': self.get_filename_timestamp(),
        })
        return context
    
    def get_filename(self, context):
        return self.filename_format.format(**context)
    
    def get_content(self, context):
        forged_catalog = self.object.get_babel_catalog()
            
        fpw = StringIO.StringIO()
        write_po(fpw, forged_catalog, sort_by_file=False, ignore_obsolete=True, include_previous=False)
        return fpw.getvalue()
