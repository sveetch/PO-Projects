# -*- coding: utf-8 -*-
"""
Models for po_projects


> Project
    |
    |_> ProjectVersion
        |
        |_> TemplateMsg
        |
        |_> Catalog
            |
            |___> TranslationMsg

"""
import json

from babel.core import Locale
from babel.messages.catalog import Catalog as BabelCatalog

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Project(models.Model):
    """
    Project container
    """
    name = models.CharField(_('name'), max_length=150)
    slug = models.SlugField(_('slug'), unique=True, max_length=75)
    description = models.TextField(_('description'), blank=True)

    def __unicode__(self):
        return self.name

    def get_current_version(self):
        return self.projectversion_set.all().annotate(catalog_count=models.Count('catalog', distinct=True)).annotate(message_count=models.Count('templatemsg', distinct=True)).order_by('-version')[0:1][0]

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

class ProjectVersion(models.Model):
    """
    Project version is what contains catalogs and template catalogs for a specific POT file version
    """
    project = models.ForeignKey(Project, verbose_name=_('project'), blank=False)
    version = models.SmallIntegerField(_('version'))
    header_comment = models.TextField(_('header comment'))
    mime_headers = models.TextField(_('mime headers'))

    def get_babel_template(self):
        """
        Return a babel template catalog suitable for a POT file
        """
        forged_catalog = BabelCatalog(
            header_comment=self.header_comment,
            project=self.project.name,
            version=str(self.version)
        )
        
        for entry in self.templatemsg_set.all().order_by('id'):
            forged_catalog.add(entry.message, string=None, locations=entry.get_locations_set(), flags=entry.get_flags_set())
        
        return forged_catalog

    def __unicode__(self):
        return "{name} v{version}".format(name=self.project.name, version=self.version)

    class Meta:
        verbose_name = _('project version')
        verbose_name_plural = _('projects versions')

class TemplateMsg(models.Model):
    """
    Template catalog item, equivalent to a msg from a POT file
    """
    project_version = models.ForeignKey(ProjectVersion, verbose_name=_('project version'), blank=False)
    message = models.TextField(_('message id'), blank=False)
    locations = models.TextField(_('locations'))
    flags = models.TextField(_('flags'))

    def __unicode__(self):
        return self.message

    def get_truncated_message(self):
        """Return truncated message to avoid message too long"""
        if not self.message:
            return ''
        elif len(self.message) <= 50:
            return self.message
        return self.message[0:50]+' [...]'
    get_truncated_message.short_description = 'Message'

    def get_locations_set(self):
        """Return a set from stored locations in JSON"""
        return set([tuple(item) for item in json.loads(self.locations)])

    def get_flags_set(self):
        """Return a set from stored flags in JSON"""
        return set(json.loads(self.flags))

    class Meta:
        verbose_name = _('template message')
        verbose_name_plural = _('templates messages')

class Catalog(models.Model):
    """
    Language catalog for a project, the PO file equivalent
    """
    project_version = models.ForeignKey(ProjectVersion, verbose_name=_('project version'), blank=False)
    locale = models.CharField(_('locale'), max_length=50, blank=False)
    header_comment = models.TextField(_('header comment'))
    mime_headers = models.TextField(_('mime headers'))

    def __unicode__(self):
        return self.get_locale_name()

    def get_locale_name(self):
        l = Locale.parse(self.locale)
        return l.english_name

    def count_empty_translations(self):
        """Return a count of translations with an empty message"""
        return self.translationmsg_set.filter(message="").count()

    def count_fuzzy_translations(self):
        """Return a count of translations with message marked as fuzzy"""
        return self.translationmsg_set.filter(fuzzy=True).count()

    def get_babel_catalog(self):
        """
        Return a babel catalog suitable for a PO file
        """
        forged_catalog = BabelCatalog(
            locale=self.locale, 
            header_comment=self.header_comment,
            project=self.project_version.project.name,
            version=str(self.project_version.version)
        )
        
        for entry in self.translationmsg_set.all().order_by('id'):
            locations = [tuple(item) for item in json.loads(entry.template.locations)]
            forged_catalog.add(entry.template.message, string=entry.message, locations=locations, flags=entry.get_flags())
        
        return forged_catalog

    class Meta:
        verbose_name = _('catalog')
        verbose_name_plural = _('catalogs')
        permissions = (
            ('edit_messages', 'Edit messages'),
        )

class TranslationMsg(models.Model):
    """
    Translation message from a catalog
    """
    template = models.ForeignKey(TemplateMsg, verbose_name=_('row source'), blank=False)
    catalog = models.ForeignKey(Catalog, verbose_name=_('catalog'), blank=False)
    message = models.TextField(_('message'), blank=True)
    fuzzy = models.BooleanField(_('fuzzy'), default=False, blank=True)
    pluralizable = models.BooleanField(_('pluralizable'), default=False, blank=True)
    python_format = models.BooleanField(_('python_format'), default=False, blank=True)

    def __unicode__(self):
        return self.message

    def get_truncated_message(self):
        """Return truncated message to avoid message too long"""
        if not self.message:
            return ''
        elif len(self.message) <= 50:
            return self.message
        return self.message[0:50]+' [...]'
    get_truncated_message.short_description = 'Message'

    def get_flags(self):
        """Return a set of flags computed from some model attributes"""
        flags = []
        if self.fuzzy: flags.append('fuzzy')
        if self.python_format: flags.append('python-format')
        return set(flags)

    class Meta:
        verbose_name = _('translation message')
        verbose_name_plural = _('translations messages')
