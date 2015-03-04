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

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from po_projects.utils import join_message_strings

class Project(models.Model):
    """
    Project container
    """
    name = models.CharField(_('name'), max_length=150)
    slug = models.SlugField(_('slug'), unique=True, max_length=75)
    domain = models.CharField(_('translation domain'), choices=settings.GETTEXT_DOMAINS, default=settings.DEFAULT_GETTEXT_DOMAINS, max_length=20)
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
        # Forge babel catalog without locale (because it's a POT)
        forged_catalog = BabelCatalog(
            header_comment=self.header_comment,
            project=self.project.name,
            domain=self.project.domain,
            version=str(self.version)
        )
        
        # Add messages to the catalog with an empty string (because it's a POT)
        for entry in self.templatemsg_set.all().order_by('id'):
            msgid = join_message_strings(entry.message, plural=entry.plural_message, pluralized=entry.pluralizable)
            forged_catalog.add(msgid, string=None, locations=entry.get_locations_set(), flags=entry.get_flags_set())
        
        return forged_catalog

    def __unicode__(self):
        return "{name} v{version}".format(name=self.project.name, version=self.version)

    class Meta:
        verbose_name = _('project version')
        verbose_name_plural = _('projects versions')



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

    def get_progress(self):
        """
        Return a percentage of progress (all filled item that are not fuzzy)
        """
        total = self.translationmsg_set.all().count()
        filled = self.translationmsg_set.exclude(message="").exclude(fuzzy=True).count()
        return (filled*100)/total

    def get_babel_catalog(self, solid=False):
        """
        Return a babel catalog suitable for a PO file
        
        ``solid`` argument is a boolean to define if the catalog also store empty and 
        fuzzy translation items (True) or drop them (False, the default)
        """
        # Forge babel catalog
        forged_catalog = BabelCatalog(
            locale=self.locale, 
            header_comment=self.header_comment,
            project=self.project_version.project.name,
            domain=self.project_version.project.domain,
            version=str(self.project_version.version)
        )
        
        queryset = self.translationmsg_set.all()
        # Exclude empty and fuzzy from queryset
        if solid:
            queryset = queryset.exclude(message="").exclude(fuzzy=True)
            
        # Add messages to the catalog using template message as "msgid" and 
        # translation message as "msgstr" with supporting plural for both of them
        for entry in queryset.order_by('id'):
            msgid = join_message_strings(entry.template.message, plural=entry.template.plural_message, pluralized=entry.template.pluralizable)
            # Use template "pluralizable" attribute because it's the reference
            msgstr = join_message_strings(entry.message, plural=entry.plural_message, pluralized=entry.template.pluralizable)
            
            # Decompile JSON value from template to get item locations
            locations = [tuple(item) for item in json.loads(entry.template.locations)]
            
            # Push the item into catalog
            forged_catalog.add(
                msgid,
                string=msgstr,
                locations=locations,
                flags=entry.get_flags()
            )
        
        return forged_catalog

    class Meta:
        verbose_name = _('catalog')
        verbose_name_plural = _('catalogs')
        permissions = (
            ('edit_messages', 'Edit messages'),
        )



class TemplateMsg(models.Model):
    """
    Template catalog item, equivalent to a msg from a POT file
    """
    project_version = models.ForeignKey(ProjectVersion, verbose_name=_('project version'), blank=False)
    message = models.TextField(_('message id'), blank=False)
    plural_message = models.TextField(_('message plural id'), blank=True, default='')
    locations = models.TextField(_('locations'))
    pluralizable = models.BooleanField(_('pluralizable'), default=False, blank=True)
    python_format = models.BooleanField(_('python_format'), default=False, blank=True)

    def __unicode__(self):
        return self.message

    def get_truncated_message(self):
        """Return truncated message to avoid too long message"""
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
        if self.python_format:
            return set(['python-format'])
        return set([])

    class Meta:
        verbose_name = _('template message')
        verbose_name_plural = _('templates messages')



class TranslationMsg(models.Model):
    """
    Translation message from a catalog
    """
    template = models.ForeignKey(TemplateMsg, verbose_name=_('row source'), blank=False)
    catalog = models.ForeignKey(Catalog, verbose_name=_('catalog'), blank=False)
    message = models.TextField(_('message'), blank=True)
    plural_message = models.TextField(_('message plural'), blank=True, default='')
    fuzzy = models.BooleanField(_('fuzzy'), default=False, blank=True)
    pluralizable = models.BooleanField(_('pluralizable'), default=False, blank=True)
    python_format = models.BooleanField(_('python format'), default=False, blank=True)

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
        if self.fuzzy:
            flags.append('fuzzy')
        if self.python_format:
            flags.append('python-format')
        return set(flags)

    class Meta:
        verbose_name = _('translation message')
        verbose_name_plural = _('translations messages')
