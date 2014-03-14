.. _django-guardian: https://github.com/lukaszb/django-guardian

**PO Projects** is a PO file management factory.

Principle is to have a frontend board to create new PO project from a POT file to import, 
then add it and manage language translations then finally export all these PO to include it 
in your app (django or another).

Features
========

* View to create new project from a PO/POT file;
* View to create new project translation and edit them;
* View to export project translations as PO files;
* View to export an archive (zip/tarball) of all translations as PO files from a project;
* Manage fuzzy mode for translations;
* Form to import a catalog (PO) to update a catalog;
* Nice frontend with Foundation;

Planned
=======

* Better model admin;
* Permission restriction (with `django-guardian`_);
* User authoring to know who has done what;
* Restricted API access to get PO files or global project archive from external tools 
  (like Optimus or a Django app from an external site) ?

External API access
===================

We should need of two clients : 

* One for Django webapp, shipped as a Django app that only exposes a command line tool, no needs of model;
* One for Optimus, allready shipped as a new command line tool;

The access to the API need to be protected and restricted to avoid that anyone can download and/or edit project translations.

API actions should be :

* Export project, this will send a tarball containing the locale directory to overwrite the one in the destination project (in the django or optimus project, not the translation project stored in Po-Projects);
* Receiving new POT file to update a project template and catalogs;

Install
=======

Add *PO Projects* to your installed apps in settings : ::

    INSTALLED_APPS = (
        ...
        'po_projects'
        ...
    )
    
Then add its settings : ::

    # Use to build path and file names in exported archive for projects
    POT_ARCHIVE_PATH = "locale/{catalog_filename}.pot"
    PO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/{catalog_filename}.po"
    
    # Available PO filename types
    DEFAULT_CATALOG_FILENAMES = 'messages'
    AVAILABLE_CATALOG_FILENAMES = ('django', 'messages')

Finally mount its urls in your main ``urls.py`` : ::

    urlpatterns = patterns('',
        ...
        (r'^po/', include('po_projects.urls', namespace='po_projects')),
        ...
    )
