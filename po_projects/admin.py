# Import from django
from django.contrib import admin

# Import from here
from .models import Project, RowSource, ProjectTranslation, RowTranslate

admin.site.register(Project)
admin.site.register(RowSource)
admin.site.register(ProjectTranslation)
admin.site.register(RowTranslate)
