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
from extra_views import ModelFormSetView

from babel.messages.pofile import write_po
from babel.messages.catalog import Catalog as BabelCatalog

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg
from po_projects.forms import ProjectForm, CatalogUpdateForm, TranslationMsgForm
from po_projects.mixins import DownloadMixin


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
            'author': self.request.user,
            'project_version': self.project_version,
        })
        return kwargs


class CatalogMessagesFormView(LoginRequiredMixin, PermissionRequiredMixin, ModelFormSetView):
    """
    Form view to edit messages from a catalog
    """
    permission_required = "po_projects.edit_messages"
    template_name = "po_projects/catalog_messages_form.html"
    model = TranslationMsg
    form_class = TranslationMsgForm
    fields = ('template','fuzzy','message',)
    extra = 0

    def get(self, request, *args, **kwargs):
        self.project = self.get_project()
        self.project_version = self.get_project_version()
        self.catalog = self.get_catalog()
        return super(CatalogMessagesFormView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project()
        self.project_version = self.get_project_version()
        self.catalog = self.get_catalog()
        return super(CatalogMessagesFormView, self).post(request, *args, **kwargs)

    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])
        
    def get_context_data(self, **kwargs):
        context = super(CatalogMessagesFormView, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'project_version': self.project_version,
            'catalog': self.catalog,
        })
        return context

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.project, version=self.kwargs['version'])
        return self.project.get_current_version()

    def get_catalog(self):
        return get_object_or_404(Catalog, project_version=self.project_version, locale=self.kwargs['locale'])

    def get_queryset(self):
        return super(CatalogMessagesFormView, self).get_queryset().select_related('template').filter(catalog=self.catalog)


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
