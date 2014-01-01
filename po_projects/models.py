# -*- coding: utf-8 -*-
"""
Models for po_projects


> Project
    |
    |____> TemplateMsg
    |____> TemplateMsg
    |____> TemplateMsg
    |
    |____> Catalog (fr)
            |
            |___> TranslationMsg
            |___> TranslationMsg
            |___> TranslationMsg
    |
    |____> Catalog (zh_hk)
            |
            |___> TranslationMsg
            |___> TranslationMsg
            |___> TranslationMsg

"""
from babel.core import Locale
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Project(models.Model):
    """
    Project contains catalog and template catalog
    """
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

class TemplateMsg(models.Model):
    """
    Template catalog item, equivalent to a msg from a POT file
    """
    project = models.ForeignKey(Project, verbose_name=_('project'), blank=False)
    message = models.TextField(_('message'), blank=False)
    locations = models.TextField(_('locations'))
    flags = models.TextField(_('flags'))

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = _('template message')
        verbose_name_plural = _('templates messages')

class Catalog(models.Model):
    """
    Language catalog for a project, the PO file equivalent
    """
    project = models.ForeignKey(Project, verbose_name=_('project'), blank=False)
    locale = models.CharField(_('locale'), max_length=50, blank=False)
    header_comment = models.TextField(_('header comment'))
    mime_headers = models.TextField(_('mime headers'))

    def __unicode__(self):
        l = Locale.parse(self.locale)
        return l.english_name

    class Meta:
        verbose_name = _('catalog')
        verbose_name_plural = _('catalogs')

class TranslationMsg(models.Model):
    """
    Translation message from a catalog
    """
    template = models.ForeignKey(TemplateMsg, verbose_name=_('row source'), blank=False)
    catalog = models.ForeignKey(Catalog, verbose_name=_('catalog'), blank=False)
    message = models.TextField(_('message'), blank=True)
    # TODO: add fuzzy boolean field

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = _('translation message')
        verbose_name_plural = _('translations messages')
