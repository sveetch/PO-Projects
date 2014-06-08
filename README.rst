.. _django-guardian: https://github.com/lukaszb/django-guardian
.. _djangorestframework: http://www.django-rest-framework.org
.. _PO-Projects-client: https://github.com/sveetch/PO-Projects-client

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
* Permission restriction;
* Restricted API access with `djangorestframework`_ to get PO files or global project 
  archive from external tools (like Optimus or a Django app from an external site) ?

Planned
=======

* User authoring to know who has done what;
* More granual permission restriction with `django-guardian`_;

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

Also to enable the rest API you will have to install `djangorestframework`_ in your settings : ::

    INSTALLED_APPS = (
        ...
        'rest_framework'
        ...
    )

    REST_FRAMEWORK = {
        'PAGINATE_BY': 10,
        # Use hyperlinked styles by default.
        # Only used if the `serializer_class` attribute is not set on a view.
        'DEFAULT_MODEL_SERIALIZER_CLASS': (
            'rest_framework.serializers.HyperlinkedModelSerializer',
        ),

        # Use Django's standard `django.contrib.auth` permissions,
        # or allow read-only access for unauthenticated users.
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAdminUser',
            #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        ),
    }

And mount it in your ``urls.py`` : ::

    urlpatterns = patterns('',
        ...
        (r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        ...
    )

External API access
===================

If `djangorestframework`_ is installed, a rest API will be available on : ::

    /po/rest/

It is browsable for authenticated users with admin rights (``is_staff`` on True), also the client will need to access to the API with an user accounts with the admin rights.

`PO-Projects-client`_ is client to use the API from your project.
