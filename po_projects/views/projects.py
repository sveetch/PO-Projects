# -*- coding: utf-8 -*-
"""
Page document views
"""
import json, os
from cStringIO import StringIO

#from django.db import models
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

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg
from po_projects.forms.project import ProjectForm, ProjectUpdateForm
from po_projects.forms.catalog import CatalogForm
from po_projects.mixins import DownloadMixin
from po_projects.dump import po_project_export

class ProjectIndex(LoginRequiredMixin, generic.TemplateView):
    """
    Project index
    """
    template_name = "po_projects/project_index.html"
    
    def get_context_data(self, **kwargs):
        context = super(ProjectIndex, self).get_context_data(**kwargs)
        context.update({
            'project_list' : Project.objects.all().order_by('name'),
        })
        return context


class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    """
    Form view to create a Project
    """
    model = Project
    template_name = "po_projects/project_form.html"
    form_class = ProjectForm
    permission_required = "po_projects.add_project"

    def get_success_url(self):
        return reverse('po_projects:project-details', args=[self.object.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectCreateView, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
        })
        return kwargs


class ProjectDetails(LoginRequiredMixin, generic.CreateView):
    """
    Form view to display Project details and append a new Catalog
    """
    model = Catalog
    template_name = "po_projects/project_details.html"
    form_class = CatalogForm

    def get(self, request, *args, **kwargs):
        self.project = self.get_project()
        self.project_version = self.get_project_version()
        return super(ProjectDetails, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project()
        self.project_version = self.get_project_version()
        return super(ProjectDetails, self).post(request, *args, **kwargs)

    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.project, version=self.kwargs['version'])
        return self.project.get_current_version()
        
    def get_context_data(self, **kwargs):
        context = super(ProjectDetails, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'project_version': self.project_version,
            'AVAILABLE_CATALOG_FILENAMES': settings.AVAILABLE_CATALOG_FILENAMES,
        })
        return context

    def get_success_url(self):
        return reverse('po_projects:project-details', args=[self.project.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectDetails, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
            'project_version': self.project_version,
        })
        return kwargs


class ProjectExportView(LoginRequiredMixin, DownloadMixin, generic.View):
    """
    View to export PO catalog files from a project into a gzip tarball
    """
    content_type = 'application/x-gzip'
    filename_format = "{project_slug}_{timestamp}.tar.gz"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.project_version = self.get_project_version()
        return super(ProjectExportView, self).get(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.object, version=self.kwargs['version'])
        return self.object.get_current_version()

    def get_domain(self):
        kind = self.request.GET.get('kind', settings.DEFAULT_CATALOG_FILENAMES)
        if kind not in settings.AVAILABLE_CATALOG_FILENAMES:
            return settings.DEFAULT_CATALOG_FILENAMES
        return kind

    def get_context_data(self, **kwargs):
        context = super(ProjectExportView, self).get_context_data(**kwargs)
        context.update({
            'project': self.object,
            'project_slug': self.object.slug,
            'timestamp': self.get_filename_timestamp(),
        })
        return context
    
    def get_filename(self, context):
        return self.filename_format.format(**context)
    
    def get_content(self, context):
        archive_file = StringIO()
        
        po_project_export(self.object, self.project_version, archive_file)
        
        return archive_file.getvalue()


class ProjectUpdate(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    """
    Form view to update project template and catalogs from a POT file
    """
    model = Project
    template_name = "po_projects/project_form.html"
    form_class = ProjectUpdateForm
    permission_required = "po_projects.change_project"

    def get(self, request, *args, **kwargs):
        self.project = self.get_project(**kwargs)
        return super(ProjectUpdate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project(**kwargs)
        return super(ProjectUpdate, self).post(request, *args, **kwargs)

    def get_project(self, **kwargs):
        return get_object_or_404(Project, slug=kwargs['slug'])
        
    def get_context_data(self, **kwargs):
        context = super(ProjectUpdate, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
        })
        return context

    def get_success_url(self):
        return reverse('po_projects:project-update', args=[self.project.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectUpdate, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
        })
        return kwargs
