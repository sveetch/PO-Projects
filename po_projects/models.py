# -*- coding: utf-8 -*-
"""
Models for po_projects
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Project(models.Model):
    name = models.CharField(_('name'), max_length=150)
    slug = models.SlugField(_('slug'), unique=True, max_length=75)
    version = models.CharField(_('version'), max_length=15)
    header_comment = models.TextField(_('header comment'))
    mime_headers = models.TextField(_('mime headers'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

class RowSource(models.Model):
    """
    TODO: should be named 'Message' instead
    """
    project = models.ForeignKey(Project, verbose_name=_('project'), blank=False)
    message = models.TextField(_('message'), blank=False)
    locations = models.TextField(_('locations'))
    flags = models.TextField(_('flags'))

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = _('row source')
        verbose_name_plural = _('row sources')

class ProjectTranslation(models.Model):
    """
    TODO: should be named 'Catalog' instead
    """
    project = models.ForeignKey(Project, verbose_name=_('project'), blank=False)
    locale = models.CharField(_('locale'), max_length=50, blank=False)
    header_comment = models.TextField(_('header comment'))
    mime_headers = models.TextField(_('mime headers'))

    def __unicode__(self):
        return self.locale

    class Meta:
        verbose_name = _('project translation')
        verbose_name_plural = _('projects translations')

class RowTranslate(models.Model):
    """
    TODO: should be named 'Translation' instead
    """
    source = models.ForeignKey(RowSource, verbose_name=_('row source'), blank=False)
    translation = models.ForeignKey(ProjectTranslation, verbose_name=_('translation'), blank=False)
    message = models.TextField(_('message'))

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = _('row translation')
        verbose_name_plural = _('row translations')
