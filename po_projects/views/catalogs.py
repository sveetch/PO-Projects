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

from po_projects.models import Project, TemplateMsg, Catalog, TranslationMsg
from po_projects.forms import ProjectForm, CatalogForm, TranslationMsgForm
from po_projects.utils import DownloadMixin


class CatalogDetails(LoginRequiredMixin, generic.UpdateView):
    """
    Form view to display Catalog details and edit its infos
    """
    model = Catalog
    template_name = "po_projects/catalog_details.html"
    form_class = CatalogForm

    def get(self, request, *args, **kwargs):
        self.project = self.get_project()
        return super(CatalogDetails, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.project = self.get_project()
        return super(CatalogDetails, self).post(request, *args, **kwargs)

    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])

    def get_object(self):
        return get_object_or_404(Catalog, project=self.project, locale=self.kwargs['locale'])
        
    def get_context_data(self, **kwargs):
        context = super(CatalogDetails, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'catalog': self.object,
        })
        return context

    def get_success_url(self):
        return reverse('po_projects:catalog-details', args=[self.project.slug, self.object.locale])

    def get_form_kwargs(self):
        kwargs = super(CatalogDetails, self).get_form_kwargs()
        kwargs.update({
            'project': self.project,
        })
        return kwargs


def CatalogMessagesFormView(request, slug=None, locale=None):
    """
    Implemented without CBV until i find HOW to do it
    """
    template_name = "po_projects/catalog_messages_form.html"
    
    project = get_object_or_404(Project, slug=slug)
    catalog = get_object_or_404(Catalog, project=project, locale=locale)
    
    formset_queryset = TranslationMsg.objects.select_related('template').filter(catalog=catalog)
    
    TranslationMsgFormSet = modelformset_factory(TranslationMsg, form=TranslationMsgForm, fields=('template','message',), extra=0)
    
    formset = TranslationMsgFormSet(request.POST or None, queryset=formset_queryset)
    
    if formset.is_valid():
        formset.save()
    
    extra_context = {
        "project": project,
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
        self.object = self.get_object()
        return super(CatalogMessagesExportView, self).get(request, *args, **kwargs)
    
    def get_project(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])

    def get_object(self):
        return get_object_or_404(Catalog, project=self.project, locale=self.kwargs['locale'])
        
    def get_context_data(self, **kwargs):
        context = super(CatalogMessagesExportView, self).get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'catalog': self.object,
            'locale_name': self.object.locale,
            'timestamp': self.get_filename_timestamp(),
        })
        return context
    
    def get_filename(self, context):
        return self.filename_format.format(**context)
    
    def get_content(self, context):
        forged_catalog = BabelCatalog(
            locale=self.object.locale, 
            header_comment=self.object.header_comment,
            project=self.project.name,
            version=self.project.version
        )
        
        for entry in self.object.translationmsg_set.all().order_by('id'):
            locations = [tuple(item) for item in json.loads(entry.template.locations)]
            forged_catalog.add(entry.template.message, string=entry.message, locations=locations, flags=entry.template.flags)
            
        fpw = StringIO.StringIO()
        write_po(fpw, forged_catalog, sort_by_file=False, ignore_obsolete=True, include_previous=False)
        return fpw.getvalue()
