# -*- coding: utf-8 -*-
"""
Root url's map for application
"""
from django.conf.urls.defaults import *

from .views import ProjectIndex, ProjectCreateView, ProjectDetails, CatalogDetails, CatalogMessagesExportView

urlpatterns = patterns('',
    url(r'^$', ProjectIndex.as_view(), name='project-index'),
    url(r'^create/$', ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<slug>[-\w]+)/$', ProjectDetails.as_view(), name='project-details'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/$', CatalogDetails.as_view(), name='catalog-details'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/edit/$', "po_projects.views.CatalogMessagesFormView", name='catalog-messages-edit'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/download/$', CatalogMessagesExportView.as_view(), name='catalog-messages-download'),
)
