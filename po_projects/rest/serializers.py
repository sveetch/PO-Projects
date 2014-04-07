"""
Serializers for REST entries
"""
from cStringIO import StringIO

from django.forms import widgets

from babel.messages.pofile import read_po

from rest_framework import serializers

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg

class VersionSerializer(serializers.ModelSerializer):
    """
    Serializer for ``ProjectVersion`` model
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-version-detail',
        lookup_field='pk'
    )
    class Meta:
        model = ProjectVersion
        fields = ('id','version','url')


class ProjectVersionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for ``Project`` model for a specific version
    
    TODO: Add tarball_url link for the given version, not for the current one
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-version-detail',
        lookup_field='pk'
    )
    tarball_url = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-archive',
        lookup_field='slug'
    )
    
    class Meta:
        model = Project
        fields = ('url', 'id', 'slug', 'name', 'description')#, 'tarball_url' )


class ProjectCurrentSerializer(ProjectVersionSerializer):
    """
    Serializer for ``Project`` model for the current version (the last one)
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='po_projects:api-project-detail',
        lookup_field='slug'
    )
    #pot_update = serializers.HyperlinkedIdentityField(
        #view_name='po_projects:api-project-pot-update',
        #lookup_field='slug'
    #)
    projectversion_set = VersionSerializer(
        many=True, read_only=True,
    )
    pot = serializers.CharField(
        widget=widgets.Textarea,
        write_only=True,
        required=False,
        help_text='(optionnal) Content for a valid POT file to update project strings to translate in its catalogs'
    )
    
    def validate_pot(self, attrs, source):
        """
        Validation for the given POT content
        """
        #print "check valid pot file"
        value = attrs[source]
        if value:
            try:
                template_file = StringIO()
                template_file.write(value)
                template_file.seek(0)
                # Seems the validation from read_po is too much minimalistic
                # This does not really valid if the content is a real POT content
                uploaded_catalog = read_po(template_file, ignore_obsolete=True)
            except:
                raise serializers.ValidationError("Your file does not seem to be a valid POT file")
        return attrs
    
    class Meta:
        model = Project
        fields = ('id', 'slug', 'name', 'description', 'url', 'tarball_url', 'pot', 'projectversion_set' )


#class ProjectPotSerializer(ProjectVersionSerializer):
    #"""
    #Serializer for ``Project`` model to update from a POT file
    #"""
    #pot = serializers.HyperlinkedIdentityField(
        #view_name='po_projects:api-project-pot-update',
        #lookup_field='slug',
        #write_only=True,
    #)
    
    #class Meta:
        #model = Project
        #fields = ('id', 'slug', 'name', 'description', 'url', 'tarball_url', 'pot' )
