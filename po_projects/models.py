# -*- coding: utf-8 -*-
"""
Models for po_projects
"""
import StringIO

from babel.core import Locale
from babel.messages.catalog import Catalog as BabelCatalog
from babel.messages.pofile import read_po

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class Project(models.Model):
    """
    Project contains template catalog (*.POT file)
    """
    created = models.DateTimeField(_('created'), blank=True, auto_now_add=True)
    author = models.ForeignKey(User, verbose_name=_('author'))
    name = models.CharField(_('name'), max_length=150)
    slug = models.SlugField(_('slug'), unique=True, max_length=75)
    version = models.CharField(_('version'), max_length=15)
    content = models.TextField(_('content'))

    def __unicode__(self):
        return self.name

    def get_babel_catalog(self):
        if not hasattr(self, "_babel_catalog"):
            setattr(self, "_babel_catalog", read_po(StringIO.StringIO(self.content), ignore_obsolete=True))
        return getattr(self, "_babel_catalog")

    def get_messages(self):
        """
        Return the list of messages from the Babel Catalog but without the first empty and fuzzy message
        """
        return list(self.get_babel_catalog())[1:]

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

class Catalog(models.Model):
    """
    Language catalog for a project, the *.PO file equivalent
    """
    modified = models.DateTimeField(_('last edit'), auto_now=True)
    author = models.ForeignKey(User, verbose_name=_('author'))
    project = models.ForeignKey(Project, verbose_name=_('project'), blank=False)
    locale = models.CharField(_('locale'), max_length=50, blank=False)
    content = models.TextField(_('content'))

    def __unicode__(self):
        l = self.get_babel_locale()
        return l.english_name

    def get_babel_locale(self):
        """Return the Babel Locale instance for the stored locale name"""
        if not hasattr(self, "_babel_locale"):
            setattr(self, "_babel_locale", Locale.parse(self.locale))
        return getattr(self, "_babel_locale")

    def get_babel_catalog(self):
        """Return the Babel Catalog instance filled from the content"""
        if not hasattr(self, "_babel_catalog"):
            setattr(self, "_babel_catalog", read_po(StringIO.StringIO(self.content), locale=self.get_babel_locale(), ignore_obsolete=True))
        return getattr(self, "_babel_catalog")

    def get_messages(self):
        """
        Return the list of messages from the Babel Catalog but without the first empty and fuzzy message
        """
        return list(self.get_babel_catalog())[1:]
    
    def percent_translated(self):
        total = len(self.get_messages())
        translated = len([item for item in self.get_messages() if (item.string and not item.fuzzy)])
        return (translated*100)/total

    class Meta:
        verbose_name = _('catalog')
        verbose_name_plural = _('catalogs')
