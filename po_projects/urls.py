# -*- coding: utf-8 -*-
"""
Root url's map for application
"""
from django.conf.urls.defaults import *

from .views import ProjectIndex, ProjectCreateView, ProjectDetails

urlpatterns = patterns('',
    url(r'^$', ProjectIndex.as_view(), name='po_projects-project-index'),
    url(r'^create/$', ProjectCreateView.as_view(), name='po_projects-project-create'),
    url(r'^(?P<slug>[-\w]+)/$', ProjectDetails.as_view(), name='po_projects-project-details'),
    #url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/$', ProjectTranslationDetails.as_view(), name='po_projects-project-translation-details'),
    url(r'^(?P<slug>[-\w]+)/(?P<locale>[-\w]+)/edit/$', "po_projects.views.TranslationFormView", name='po_projects-translation-edit'),
)
