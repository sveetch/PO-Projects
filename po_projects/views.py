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

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from babel.messages.pofile import read_po

from .models import Project, RowSource, ProjectTranslation, RowTranslate
from .forms import ProjectForm, ProjectTranslationForm, RowTranslationForm

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
        return reverse('po_projects-project-details', args=[self.object.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectCreateView, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
        })
        return kwargs

class ProjectDetails(LoginRequiredMixin, generic.CreateView):
    """
    Form view to display Project details and append a new project translations
    """
    model = ProjectTranslation
    template_name = "po_projects/project_details.html"
    form_class = ProjectTranslationForm

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
        return reverse('po_projects-project-details', args=[self.project.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectDetails, self).get_form_kwargs()
        kwargs.update({
            'project': self.project,
        })
        return kwargs

class ProjectTranslationDetails(LoginRequiredMixin, generic.CreateView):
    """
    Form view to display Project translation details and edit its message translations
    
    DEPRECATED: not unable to find how to implement modelformset within CBV
    """
    model = ProjectTranslation
    template_name = "po_projects/project-translation_details.html"
    form_class = RowTranslationForm # TODO: formset

    def get(self, request, *args, **kwargs):
        self.project = self.get_project(**kwargs)
        self.translation = self.get_translation(**kwargs)
        return super(ProjectTranslationDetails, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project(**kwargs)
        return super(ProjectTranslationDetails, self).post(request, *args, **kwargs)

    def get_project(self, **kwargs):
        return get_object_or_404(Project, slug=kwargs['slug'])
        
    def get_translation(self, **kwargs):
        return get_object_or_404(ProjectTranslation, project=self.project, locale=kwargs['locale'])
        
    def get_context_data(self, **kwargs):
        context = super(ProjectTranslationDetails, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'translation': self.translation,
        })
        return context

    def get_success_url(self):
        return reverse('po_projects-project-details', args=[self.project.slug])

    def get_form_kwargs(self):
        kwargs = super(ProjectTranslationDetails, self).get_form_kwargs()
        kwargs.update({
            'translation': self.translation,
        })
        return kwargs

from django.forms.models import modelformset_factory
def TranslationFormView(request, slug=None, locale=None):
    template_name = "po_projects/translation_formset_edit.html"
    
    project = get_object_or_404(Project, slug=slug)
    translation = get_object_or_404(ProjectTranslation, project=project, locale=locale)
    
    formset_queryset = RowTranslate.objects.select_related('source').filter(translation=translation)
    
    RowTranslationFormSet = modelformset_factory(RowTranslate, form=RowTranslationForm, fields=('source','message',), extra=0)
    
    formset = RowTranslationFormSet(request.POST or None, queryset=formset_queryset)
    
    if formset.is_valid():
        formset.save()
    #else:
        #print formset.errors
    
    extra_context = {
        "project": project,
        "translation": translation,
        "formset": formset
    }
    return render_to_response(template_name, extra_context, context_instance=RequestContext(request))
