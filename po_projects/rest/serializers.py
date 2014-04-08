"""
Serializers for REST entries
"""
from cStringIO import StringIO

from django.forms import widgets

from babel.messages.pofile import read_po

from rest_framework import serializers

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg
from po_projects.utils import create_templatemsgs, create_new_version, update_catalogs

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
        value = attrs[source]
        if value:
            try:
                template_file = StringIO()
                template_file.write(value.encode('UTF8'))
                template_file.seek(0)
                # Seems the validation from read_po is too much minimalistic
                # This does not really valid if the content is a real POT content
                self.uploaded_pot_file = read_po(template_file, ignore_obsolete=True)
            except:
                raise serializers.ValidationError("Your file does not seem to be a valid POT file")
        return attrs

    def save(self, **kwargs):
        """
        Override the save method to update template and catalog from the given POT
        """
        super(ProjectCurrentSerializer, self).save(**kwargs)
        
        if hasattr(self, 'uploaded_pot_file'):
            previous_version = self.object.get_current_version()
            current_version = create_new_version(self.object, previous_version.version+1, self.uploaded_pot_file)
            update_catalogs(self.object, previous_version, current_version)
            self.object.save()
         
        return self.object
    
    class Meta:
        model = Project
        fields = ('id', 'slug', 'name', 'description', 'url', 'tarball_url', 'pot', 'projectversion_set' )
