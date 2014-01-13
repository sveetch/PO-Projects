# -*- coding: utf-8 -*-
"""
Root url's map for application
"""
from django.conf.urls.defaults import *

from po_projects.views.projects import ProjectIndex, ProjectCreateView, ProjectDetails, ProjectExportView, ProjectUpdate
from po_projects.views.catalogs import CatalogDetails, CatalogMessagesExportView

urlpatterns = patterns('',
    url(r'^$', ProjectIndex.as_view(), name='project-index'),
    
    url(r'^create/$', ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<slug>[-\w]+)/$', ProjectDetails.as_view(), name='project-details'),
    url(r'^(?P<slug>[-\w]+)/update/$', ProjectUpdate.as_view(), name='project-update'),
    url(r'^(?P<slug>[-\w]+)/download/$', ProjectExportView.as_view(), name='project-download'),
    
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/$', CatalogDetails.as_view(), name='catalog-details'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/edit/$', "po_projects.views.catalogs.CatalogMessagesFormView", name='catalog-messages-edit'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/download/$', CatalogMessagesExportView.as_view(), name='catalog-messages-download'),
)
