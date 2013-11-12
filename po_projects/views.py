# -*- coding: utf-8 -*-
"""
Page document views
"""
import os

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

from babel.messages.pofile import read_po

from .models import Project, Catalog
from .forms import ProjectForm, ProjectUpdateForm, CatalogForm, CatalogMessagesForm

class ProjectIndexView(generic.TemplateView):
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
    form_class = ProjectForm
    template_name = "po_projects/project_form.html"

    def get_success_url(self):
        return reverse('po_projects:project-details', args=[self.object.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectCreateView, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
        })
        return kwargs

class ProjectDetailsView(LoginRequiredMixin, generic.CreateView):
    """
    Form view to display Project details and append a new Catalog
    """
    model = Catalog
    form_class = CatalogForm
    template_name = "po_projects/project_details.html"

    def get(self, request, *args, **kwargs):
        self.project = self.get_project(**kwargs)
        return super(ProjectDetailsView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project(**kwargs)
        return super(ProjectDetailsView, self).post(request, *args, **kwargs)

    def get_project(self, **kwargs):
        return get_object_or_404(Project, slug=kwargs['slug'])

    def get_success_url(self):
        return reverse('po_projects:project-details', args=[self.project.slug])
        
    def get_context_data(self, **kwargs):
        context = super(ProjectDetailsView, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(ProjectDetailsView, self).get_form_kwargs()
        kwargs.update({
            'project': self.project,
            'author': self.request.user,
        })
        return kwargs

class ProjectMessagesView(LoginRequiredMixin, generic.UpdateView):
    """
    Form view to update the template catalog all project's catalog
    with a POT file
    """
    model = Project
    form_class = ProjectUpdateForm
    template_name = "po_projects/project_messages.html"

    def get_success_url(self):
        return reverse('po_projects:project-messages', args=[self.object.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectMessagesView, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
        })
        return kwargs

class CatalogDetailsView(LoginRequiredMixin, generic.UpdateView):
    """
    Form view to display Project details and append a new Catalog
    """
    model = Catalog
    form_class = CatalogForm
    template_name = "po_projects/catalog_details.html"

    def get(self, request, *args, **kwargs):
        self.project = self.get_project()
        return super(CatalogDetailsView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project()
        return super(CatalogDetailsView, self).post(request, *args, **kwargs)

    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])

    def get_object(self):
        return get_object_or_404(Catalog, project=self.project, locale=self.kwargs['locale'])
        
    def get_context_data(self, **kwargs):
        context = super(CatalogDetailsView, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'catalog': self.object,
        })
        return context

    def get_success_url(self):
        return reverse('po_projects:catalog-details', args=[self.project.slug, self.object.locale])

    def get_form_kwargs(self):
        kwargs = super(CatalogDetailsView, self).get_form_kwargs()
        kwargs.update({
            'project': self.project,
            'author': self.request.user,
        })
        return kwargs

class CatalogMessagesEditView(LoginRequiredMixin, generic.UpdateView):
    """
    Catalog message list form
    """
    model = Catalog
    form_class = CatalogMessagesForm
    template_name = "po_projects/catalog_messages.html"

    def get(self, request, *args, **kwargs):
        self.project = self.get_project()
        return super(CatalogMessagesEditView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project()
        return super(CatalogMessagesEditView, self).post(request, *args, **kwargs)

    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])
    
    def get_object(self, queryset=None):
        return get_object_or_404(Catalog, project=self.project, locale=self.kwargs['locale'])
        
    def get_context_data(self, **kwargs):
        context = super(CatalogMessagesEditView, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'catalog': self.object,
        })
        return context

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = {}
        for i, msg in enumerate(self.object.get_messages()):
            initial['msg_{0}'.format(i)] = msg.string
            
        return initial.copy()

    def get_success_url(self):
        return reverse('po_projects:catalog-messages-edit', args=[self.project.slug, self.object.locale])

    def get_form_kwargs(self):
        kwargs = super(CatalogMessagesEditView, self).get_form_kwargs()
        kwargs.update({
            'project': self.project,
            'author': self.request.user,
        })
        return kwargs
