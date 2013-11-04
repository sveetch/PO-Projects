# -*- coding: utf-8 -*-
"""
General Command line tool
"""
import StringIO, json

from optparse import OptionValueError, make_option

from babel.messages.pofile import read_po
from babel import Locale
from babel.core import UnknownLocaleError, get_locale_identifier

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import CommandError, BaseCommand

from apps.po_projects.models import Project, RowSource, RowTranslate

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--source", dest="source_filepath", default=None, help="Source to import."),
        #make_option("--clearcache", dest="clearcache", action="store_true", default=False, help="Clear all documents (Page and Insert) cache."),
    )
    help = "PO Project CLI"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.source_filepath = options.get('source_filepath')
        self.verbosity = int(options.get('verbosity'))
        
        self.just_do_it()

    def just_do_it(self):
        self.locale_tuple()

    def locale_tuple(self):
        """
        Method to some dev/test/debug
        """
        l = Locale.parse('en-AU')
        print "language:", l.language
        print "territory:", l.territory
        print "script:", l.script
        print "variant:", l.variant
        
        print get_locale_identifier((l.language, l.territory, l.script, l.variant), sep='_')

    def check_locale(self):
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
