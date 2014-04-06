"""
REST API

TODO: Include the following doc to the README

Install `djangorestframework`_

Add this to your settings : ::

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
    
And this to **your project's urls.py** : ::

    urlpatterns = patterns('',
        ...
        (r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        ...
    )

Then the API is reachable from ``http://yoururl/po/rest/`` that will display available endpoints. You must be authenticated to access to the API.

Actually this will serve some endpoints :

* Project list
* Project detail to retrieve or update (TODO) a Project instance
* Project tarball (but for the last version only)
"""
