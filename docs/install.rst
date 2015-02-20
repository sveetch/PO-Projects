.. _Django: https://www.djangoproject.com/
.. _djangorestframework: http://www.django-rest-framework.org
.. _PO-Projects-client: https://github.com/sveetch/PO-Projects-client

=======
Install
=======

Add *PO Projects* to your installed apps in settings : ::

    INSTALLED_APPS = (
        ...
        'po_projects'
        ...
    )
    
Then import its default settings : ::

    from po_projects.settings import *

If needed you can override some of its settings, see the original file to watch about available settings.

Finally mount its urls in your main ``urls.py`` : ::

    urlpatterns = patterns('',
        ...
        (r'^po/', include('po_projects.urls', namespace='po_projects')),
        ...
    )

External API access
===================

To enable the rest API you will have to install `djangorestframework`_ in your settings : ::

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

And so a rest API will be available on : ::

    /po/rest/

It is browsable for authenticated users with admin rights (``is_staff`` on True), also the client will need to access to the API with an user accounts with the admin rights.

`PO-Projects-client`_ is the client to use the API from your project.

