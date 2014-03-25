"""
Serializers for REST entries
"""
from rest_framework import serializers

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg


#class CustomHyperlinkedField(serializers.HyperlinkedRelatedField):
    #def get_url(self, obj, view_name, request, format):
        #kwargs = {'locale': obj.locale, 'slug': obj.slug}
        #return reverse(view_name, kwargs=kwargs, request=request, format=format)

    #def get_object(self, queryset, view_name, view_args, view_kwargs):
        #locale = view_kwargs['locale']
        #slug = view_kwargs['slug']
        #return queryset.get(locale=locale, slug=slug)


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-detail',
        lookup_field='slug'
    )
    tarball = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-archive',
        lookup_field='slug'
    )
    projectversion_set = serializers.RelatedField(many=True)
    
    #projectversion_set = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='track-detail')
    
    class Meta:
        model = Project
        fields = ('url', 'id', 'slug', 'name', 'description', 'tarball', 'projectversion_set' )
