# -*- coding: utf-8 -*-
"""
Root url's map for application
"""
from django.conf.urls.defaults import *

from .views import ProjectIndexView, ProjectCreateView, ProjectDetailsView, ProjectMessagesView, CatalogDetailsView, CatalogMessagesEditView

urlpatterns = patterns('',
    url(r'^$', ProjectIndexView.as_view(), name='project-index'),
    url(r'^create/$', ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<slug>[-\w]+)/$', ProjectDetailsView.as_view(), name='project-details'),
    url(r'^(?P<slug>[-\w]+)/messages/$', ProjectMessagesView.as_view(), name='project-messages'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/$', CatalogDetailsView.as_view(), name='catalog-details'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/edit/$', CatalogMessagesEditView.as_view(), name='catalog-messages-edit'),
)
