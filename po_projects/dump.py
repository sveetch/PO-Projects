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

def po_project_export(project, project_version, archive_fileobj, catalog_filename):
    """
    Export all catalogs from a project into PO files with the good directory 
    structure
    """
    archive_files = []
    
    # Template catalog POT file
    template_file = StringIO()
    write_po(template_file, project_version.get_babel_template(), sort_by_file=False, ignore_obsolete=True, include_previous=False)
    template_file.seek(0)
    archive_files.append( (settings.POT_ARCHIVE_PATH.format(catalog_filename=catalog_filename), template_file) )
    
    # Catalog PO files
    for catalog in project_version.catalog_set.all():
        archived_path = settings.PO_ARCHIVE_PATH.format(locale=catalog.locale, catalog_filename=catalog_filename)
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

