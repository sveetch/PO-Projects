"""
Serializers for REST entries
"""
from rest_framework import serializers

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg

class VersionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-version-detail',
        lookup_field='pk'
    )
    class Meta:
        model = ProjectVersion
        fields = ('id','version','url')


class ProjectVersionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-version-detail',
        lookup_field='pk'
    )
    tarball = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-archive',
        lookup_field='slug'
    )
    
    class Meta:
        model = Project
        fields = ('url', 'id', 'slug', 'name', 'description', 'tarball' )


class ProjectCurrentSerializer(ProjectVersionSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-detail',
        lookup_field='slug'
    )
    projectversion_set = VersionSerializer(
        many=True, read_only=True,
    )
    
    class Meta:
        model = Project
        fields = ('url', 'id', 'slug', 'name', 'description', 'tarball', 'projectversion_set' )
