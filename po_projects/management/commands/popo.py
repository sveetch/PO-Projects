# -*- coding: utf-8 -*-
"""
Just a command line to test some things in development
"""
from cStringIO import StringIO
import json, os, tarfile, time

from optparse import OptionValueError, make_option

from babel.messages.pofile import read_po, write_po
from babel import Locale
from babel.core import UnknownLocaleError, get_locale_identifier
from babel.messages.catalog import Catalog as BabelCatalog

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import CommandError, BaseCommand

from po_projects.models import Project, Catalog, TranslationMsg
from po_projects.dump import po_project_export

PO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/messages.po"

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--source", dest="source_filepath", default=None, help="Source to import."),
        make_option("--project", dest="project_slug", default=None, help="Project slug to export"),
    )
    help = "PO Project CLI"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.source_filepath = options.get('source_filepath')
        self.project_slug = options.get('project_slug')
        self.verbosity = int(options.get('verbosity'))
        
        self.just_do_it()

    def just_do_it(self):
        self.do_po_project_export()

    def do_po_project_export(self):
        """
        Export all catalogs from a project into PO files with the good directory 
        structure
        """
        if not self.project_slug:
            raise CommandError("project slug is empty")
        
        # Open and fill tarball archive
        #archive_file = StringIO()
        archive_file = open("{0}.tar.gz".format(self.project_slug), "wb")
        
        po_project_export(self.project_slug, archive_file)
        
        archive_file.close()

    def po_catalog_export(self):
        """
        Export a catalog from a project into a PO file
        """
        toast_path = "/home/django/Emencia/po_headquarter/dummy_po/"
        
        project = Project.objects.get(slug='dummy')
        catalog = Catalog.objects.get(project=project, locale='fr')
        
        #mime_dict = json.loads(catalog.mime_headers)
        
        forged_catalog = BabelCatalog(
            locale=catalog.locale, 
            header_comment=catalog.header_comment,
            project=project.name,
            version="0.2.0"
        )
        
        print "before add:", len(forged_catalog)
        
        for entry in catalog.translationmsg_set.all().order_by('id'):
            locations = [tuple(item) for item in json.loads(entry.template.locations)]
            forged_catalog.add(entry.template.message, string=entry.message, locations=locations, flags=entry.template.flags)
        
        print "after add:", len(forged_catalog)
        print "errors:", [item for item in forged_catalog.check()]
        
        print
        print "---------------- Original"
        fpw = StringIO()
        write_po(fpw, forged_catalog, sort_by_file=False, ignore_obsolete=True, include_previous=False)
        print fpw.getvalue()
        fpw.close()
        
        print
        print "---------------- Updated"
        fp3 = open(os.path.join(toast_path, '0-3-0.pot'), 'r')
        template_catalog_3 = read_po(fp3)
        forged_catalog.update(template_catalog_3)
        
        fpw = StringIO()
        write_po(fpw, forged_catalog, sort_by_file=False, ignore_obsolete=True, include_previous=False)
        print fpw.getvalue()
        fpw.close()

    def po_update(self):
        """
        Testing PO file update with another PO file
        """
        toast_path = "/home/django/Emencia/po_headquarter/dummy_po/"
        
        project = Project.objects.get(slug='dummy')
        catalog = Catalog.objects.get(project=project, locale='fr')
        
        fp1 = open(os.path.join(toast_path, '0-1-0.pot'), 'r')
        fp2 = open(os.path.join(toast_path, '0-2-0.pot'), 'r')
        
        template_catalog_1 = read_po(fp1)
        template_catalog_2 = read_po(fp2)
        
        #print "before update:", len(catalog)
        template_catalog_1.update(template_catalog_2)
        #print "after update:", len(catalog)
        
        print catalog

    def locale_tuple(self):
        """
        Testing locale identifier parsing attributes
        """
        l = Locale.parse('en-AU')
        print "language:", l.language
        print "territory:", l.territory
        print "script:", l.script
        print "variant:", l.variant
        
        print get_locale_identifier((l.language, l.territory, l.script, l.variant), sep='_')

    def check_locale(self):
        """
        Testing locale identifier parsing with error
        """
        print Locale.parse('fr')
        try:
            print Locale.parse('francais')
        except ValueError:
            print 'ValueError!'
        except UnknownLocaleError:
            print 'UnknownLocaleError!'
        print Locale.parse('zh_CN')
        print Locale.parse('en_AU')

    def open_po(self):
        """
        Testing PO file opening with --source CLI argument
        """
        if self.source_filepath:
            fp = open(self.source_filepath, "r")
            try:
                catalog = read_po(fp)
            except:
                raise CommandError("Invalid PO file")
            else:
                print catalog.project
                print json.dumps(catalog.mime_headers, indent=4)
            finally:
                fp.close()
        else:
            raise CommandError("Command action need the --source argument")
