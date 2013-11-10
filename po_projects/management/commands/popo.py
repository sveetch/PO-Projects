# -*- coding: utf-8 -*-
"""
General Command line tool
"""
import StringIO, json, os

from optparse import OptionValueError, make_option

from babel.messages.pofile import read_po, write_po
from babel import Locale
from babel.core import UnknownLocaleError, get_locale_identifier
from babel.messages.catalog import Catalog as BabelCatalog

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import CommandError, BaseCommand

from po_projects.models import Project, Catalog, TranslationMsg

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--source", dest="source_filepath", default=None, help="Source to import."),
        make_option("--target", dest="target_filepath", default=None, help="Path to write exported file"),
        #make_option("--clearcache", dest="clearcache", action="store_true", default=False, help="Clear all documents (Page and Insert) cache."),
    )
    help = "PO Project CLI"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.source_filepath = options.get('source_filepath')
        self.target_filepath = options.get('target_filepath')
        self.verbosity = int(options.get('verbosity'))
        
        self.just_do_it()

    def just_do_it(self):
        self.po_export()

    def po_export(self):
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
        fpw = StringIO.StringIO()
        write_po(fpw, forged_catalog, sort_by_file=False, ignore_obsolete=True, include_previous=False)
        print fpw.getvalue()
        fpw.close()
        
        print
        print "---------------- Updated"
        fp3 = open(os.path.join(toast_path, '0-3-0.pot'), 'r')
        template_catalog_3 = read_po(fp3)
        forged_catalog.update(template_catalog_3)
        
        fpw = StringIO.StringIO()
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
