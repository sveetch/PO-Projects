# -*- coding: utf-8 -*-
"""
Root url's map for application
"""
from django.conf.urls import *

from po_projects.views.projects import ProjectIndex, ProjectCreateView, ProjectDetails, ProjectExportView, ProjectUpdate
from po_projects.views.catalogs import CatalogDetails, CatalogMessagesExportView, CatalogMessagesFormView

urlpatterns = patterns('',
    url(r'^$', ProjectIndex.as_view(), name='project-index'),
    
    url(r'^create/$', ProjectCreateView.as_view(), name='project-create'),
    url(r'^(?P<slug>[-\w]+)/$', ProjectDetails.as_view(), name='project-details'),
    url(r'^(?P<slug>[-\w]+)/update/$', ProjectUpdate.as_view(), name='project-update'),
    url(r'^(?P<slug>[-\w]+)/download/$', ProjectExportView.as_view(), name='project-download'),
    
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/$', CatalogDetails.as_view(), name='catalog-details'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/edit/$', CatalogMessagesFormView.as_view(), name='catalog-messages-edit'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/download/$', CatalogMessagesExportView.as_view(), name='catalog-messages-download'),
)

"""
Urls map for API with Django REST Framework if installed

TODO: 

* project update from a POT file
* get project catalogs tarball

"""
try:
    from rest_framework.urlpatterns import format_suffix_patterns
except ImportError:
    pass
else:
    from po_projects.rest import views

    rest_urlpatterns = format_suffix_patterns(patterns('po_projects.rest.views',
        url(r'^rest/$', 'api_root'),
        url(r'^rest/projects/$', views.ProjectList.as_view(), name='api-project-list'),
        url(r'^rest/projects/current/(?P<slug>[-\w]+)/$', views.ProjectCurrentDetail.as_view(), name='api-project-detail'),
        url(r'^rest/projects/current/(?P<slug>[-\w]+)/tarball/$', views.ProjectArchive.as_view(), name='api-project-archive'),
        #url(r'^rest/projects/current/(?P<slug>[-\w]+)/pot-update/$', views.ProjectCurrentDetail.as_view(), name='api-project-pot-update'),
        url(r'^rest/projects/version/(?P<pk>\d+)/$', views.ProjectVersionDetail.as_view(), name='api-project-version-detail'),
    ))

    urlpatterns = rest_urlpatterns + urlpatterns
