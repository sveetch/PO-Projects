# Import from django
from django.contrib import admin

# Import from here
from .models import Project, Catalog

admin.site.register(Project)
admin.site.register(Catalog)
