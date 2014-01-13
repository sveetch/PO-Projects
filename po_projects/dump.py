# -*- coding: utf-8 -*-
"""
Dump tools
"""
from cStringIO import StringIO
import json, os, tarfile, time

from babel.messages.pofile import write_po
from babel import Locale
from babel.core import UnknownLocaleError, get_locale_identifier
from babel.messages.catalog import Catalog as BabelCatalog

from django.conf import settings

from po_projects.models import Project, Catalog

POT_ARCHIVE_PATH = "locale/messages.pot"
PO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/messages.po"

def po_project_export(project_slug, archive_fileobj):
    """
    Export all catalogs from a project into PO files with the good directory 
    structure
    
    TODO: * accept a project slug OR a project instance (to avoid to get it again from database)
    """
    #print "Project :", project_slug
    project = Project.objects.get(slug=project_slug)
    #print "- name :", project.name
    
    archive_files = []
    
    # Template catalog POT file
    template_file = StringIO()
    write_po(template_file, project.get_babel_template(), sort_by_file=False, ignore_obsolete=True, include_previous=False)
    template_file.seek(0)
    archive_files.append( (POT_ARCHIVE_PATH, template_file) )
    
    # Catalog PO files
    for catalog in project.catalog_set.all():
        archived_path = PO_ARCHIVE_PATH.format(locale=catalog.locale)
        #print " * Catalog:", catalog.locale
        #print "     - Path :", archived_path
        # Open a new catalog
        babel_catalog = catalog.get_babel_catalog()
        # Write it to a buffer string
        catalog_file = StringIO()
        write_po(catalog_file, babel_catalog, sort_by_file=False, ignore_obsolete=True, include_previous=False)
        catalog_file.seek(0)
        
        archive_files.append( (archived_path, catalog_file) )
    
    # Open and fill tarball archive
    archive = tarfile.open("{0}.tar.gz".format(project.slug), mode="w:gz", fileobj=archive_fileobj)
    mtime = time.time()
    
    for name,content in archive_files:
        info = tarfile.TarInfo(name)
        info.size=len(content.getvalue())
        info.mtime = mtime
        archive.addfile(tarinfo=info, fileobj=content)
        #
        content.close()
    
    archive.close()
    
    return archive_fileobj

