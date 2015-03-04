from django.contrib import admin
from .models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg

class ProjectAdmin(admin.ModelAdmin):
    ordering = ('name',)
    search_fields = ('slug', 'name',)
    list_display = ('slug', 'name')
    prepopulated_fields = {"slug": ("name",)}
    
class ProjectVersionAdmin(admin.ModelAdmin):
    ordering = ('project', 'version',)
    list_filter = ('project',)
    #list_display = ('version', 'project',)
    fieldsets = (
        (None, {
            'fields': ('project', 'version')
        }),
        ('Metas', {
            'classes': ('collapse',),
            'fields': ('header_comment', 'mime_headers')
        }),
    )
    
class CatalogAdmin(admin.ModelAdmin):
    ordering = ('project_version', 'locale',)
    list_filter = ('project_version__project',)
    list_display = ('project_version', 'locale',)
    list_display_links = ('project_version', 'locale',)
    raw_id_fields = ("project_version",)
    fieldsets = (
        (None, {
            'fields': ('project_version', 'locale')
        }),
        ('Metas', {
            'classes': ('collapse',),
            'fields': ('header_comment', 'mime_headers')
        }),
    )
    
class TemplateMsgAdmin(admin.ModelAdmin):
    ordering = ('project_version', 'message',)
    list_filter = ('project_version__project', 'pluralizable', 'python_format')
    list_display = ('project_version', 'pluralizable', 'python_format', 'get_truncated_message',)
    raw_id_fields = ("project_version",)
    search_fields = ('message', 'plural_message')
    fieldsets = (
        (None, {
            'fields': ('project_version', 'message', 'plural_message')
        }),
        ('Metas', {
            'fields': ('locations', 'pluralizable', 'python_format')
        }),
    )
    
class TranslationMsgAdmin(admin.ModelAdmin):
    ordering = ('catalog', 'message',)
    list_filter = ('catalog__project_version__project', 'fuzzy', 'pluralizable', 'python_format')
    list_display = ('catalog', 'fuzzy', 'pluralizable', 'python_format', 'get_truncated_message',)
    list_display_links = ('catalog', 'get_truncated_message',)
    raw_id_fields = ("template","catalog",)
    search_fields = ('message', 'plural_message')
    fieldsets = (
        (None, {
            'fields': ('template', 'catalog')
        }),
        ('Content', {
            'fields': ('message', 'plural_message')
        }),
        ('Options', {
            'fields': ('fuzzy', 'pluralizable', 'python_format')
        }),
    )


admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectVersion, ProjectVersionAdmin)
admin.site.register(TemplateMsg, TemplateMsgAdmin)
admin.site.register(Catalog, CatalogAdmin)
admin.site.register(TranslationMsg, TranslationMsgAdmin)
