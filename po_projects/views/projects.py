# -*- coding: utf-8 -*-
"""
Page document views
"""
import json, os
from cStringIO import StringIO

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

from po_projects.models import Project, TemplateMsg, Catalog, TranslationMsg
from po_projects.forms import ProjectForm, CatalogForm, TranslationMsgForm
from po_projects.utils import DownloadMixin
from po_projects.dump import po_project_export

class ProjectIndex(generic.TemplateView):
    """
    Project index
    """
    template_name = "po_projects/project_index.html"
    
    def get(self, request, *args, **kwargs):
        context = {'project_list' : Project.objects.all().order_by('name')}
        return self.render_to_response(context)


#class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    """
    Form view to create a Project
    """
    model = Project
    template_name = "po_projects/project_form.html"
    form_class = ProjectForm

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
        self.project = self.get_project(**kwargs)
        return super(ProjectDetails, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project(**kwargs)
        return super(ProjectDetails, self).post(request, *args, **kwargs)

    def get_project(self, **kwargs):
        return get_object_or_404(Project, slug=kwargs['slug'])
        
    def get_context_data(self, **kwargs):
        context = super(ProjectDetails, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
        })
        return context

    def get_success_url(self):
        return reverse('po_projects:project-details', args=[self.project.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectDetails, self).get_form_kwargs()
        kwargs.update({
            'project': self.project,
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
        return super(ProjectExportView, self).get(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])

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
        
        # TODO: give directly the project instance not its slug
        po_project_export(self.object.slug, archive_file)
        
        #archive_file.close()
        return archive_file.getvalue()
