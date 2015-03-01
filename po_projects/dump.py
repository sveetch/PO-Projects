# -*- coding: utf-8 -*-
"""
Dump tools
"""
from cStringIO import StringIO
import json, os, tarfile, time

from babel.messages.pofile import write_po
from babel.messages.mofile import write_mo
from babel import Locale
from babel.core import UnknownLocaleError, get_locale_identifier
from babel.messages.catalog import Catalog as BabelCatalog

from django.conf import settings

from po_projects.models import Project, Catalog

def po_project_export(project, project_version, archive_fileobj, compile_mo=True):
    """
    Export all catalogs from a project into PO files with the good directory 
    structure
    
    NOTE: One improvement would be to not perform two querysets for each catalog (one for PO, one 'solid' for MO)
    """
    archive_files = []
    
    # Template catalog POT file
    template_file = StringIO()
    write_po(template_file, project_version.get_babel_template(), sort_by_file=False, ignore_obsolete=True, include_previous=False)
    template_file.seek(0)
    archive_files.append( (settings.POT_ARCHIVE_PATH.format(catalog_filename=project.domain), template_file) )
    
    # Catalog PO files
    for catalog in project_version.catalog_set.all():
        po_file_path = settings.PO_ARCHIVE_PATH.format(locale=catalog.locale, catalog_filename=project.domain)
        mo_file_path = settings.MO_ARCHIVE_PATH.format(locale=catalog.locale, catalog_filename=project.domain)
        
        # Write the PO to a buffer string
        po_file = StringIO()
        write_po(po_file, catalog.get_babel_catalog(), sort_by_file=False, ignore_obsolete=True, include_previous=False)
        po_file.seek(0)
        
        # Append the PO file to the archive manifest
        archive_files.append( (po_file_path, po_file) )
        
        # Write the MO to a buffer string
        mo_file = StringIO()
        write_mo(mo_file, catalog.get_babel_catalog(solid=True), use_fuzzy=False)
        mo_file.seek(0)
        
        # Append the MO file to the archive manifest
        archive_files.append( (mo_file_path, mo_file) )
        
    
    # Open and fill tarball archive
    archive = tarfile.open("{0}.tar.gz".format(project.slug), mode="w:gz", fileobj=archive_fileobj)
    mtime = time.time()
    
    # Build the tarball from the manifest
    for name,content in archive_files:
        info = tarfile.TarInfo(name)
        info.size=len(content.getvalue())
        info.mtime = mtime
        archive.addfile(tarinfo=info, fileobj=content)
        #
        content.close()
    
    archive.close()
    
    return archive_fileobj

