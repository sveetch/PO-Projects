# -*- coding: utf-8 -*-
"""
Command line tool to export project files
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

from po_projects.models import Project, Catalog

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--project", dest="project_slug", default=None, help="Project slug"),
        make_option("--target", dest="target_filepath", default=os.getcwd(), help="Path to export project PO directory"),
    )
    help = "PO Project export"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.target_filepath = options.get('target_filepath')
        self.verbosity = int(options.get('verbosity'))
        
        if not options.get('project_slug'):
            raise CommandError("Command require at least the --project argument")
        
        try:
            self.project = Project.objects.get(slug=options.get('project_slug'))
        except Project.DoesNotExist:
            raise CommandError("There is no project with the given slug '{0}'".format(options.get('project_slug')))
        
        self.just_do_it()

    def just_do_it(self):
        locale_basepath = os.path.join(self.target_filepath, "locale")
        catalog_dir_string = "{locale}/LC_MESSAGES"
        
        if os.path.exists(locale_basepath):
            raise CommandError("A directory allready exists at '{0}'".format(locale_basepath))
        
        print locale_basepath
        os.makedirs(locale_basepath)
        print "", "messages.pot"
        fpw = open(os.path.join(locale_basepath, "messages.pot"), "w")
        fpw.write(self.project.content)
        fpw.close()
        
        for catalog in self.project.catalog_set.all().order_by('locale'):
            catalog_dir = catalog_dir_string.format(locale=catalog.locale)
            catalog_path = os.path.join(locale_basepath, catalog_dir)
            
            os.makedirs(catalog_path)
            print "*", catalog_path
            print "", "-", "messages.po"
            
            fpw = open(os.path.join(catalog_path, "messages.po"), "w")
            fpw.write(catalog.content)
            fpw.close()
        
