# Import from django
from django.contrib import admin

# Import from here
from .models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg

admin.site.register(Project)
admin.site.register(ProjectVersion)
admin.site.register(TemplateMsg)
admin.site.register(Catalog)
admin.site.register(TranslationMsg)
