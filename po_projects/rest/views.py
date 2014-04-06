from cStringIO import StringIO

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, viewsets, generics, renderers
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg
from po_projects.rest.serializers import ProjectCurrentSerializer, ProjectVersionSerializer
from po_projects.utils import DownloadMixin
from po_projects.dump import po_project_export

@api_view(('GET',))
def api_root(request, format=None):
    """
    This is the entry point that display available endpoints for this API
    """
    return Response({
        'projects': reverse('po_projects:api-project-list', request=request, format=format)
    })


class ProjectList(APIView):
    """
    List all available projects
    """
    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectCurrentSerializer(projects, many=True, context={'request': request})

        return Response(serializer.data)


class ProjectCurrentDetail(generics.RetrieveUpdateAPIView):
    """
    Retrieve the current last version of a project instance from its slug. 
    
    * ``projectversion_set`` attribute will contains the project versions;
    * ``tarball`` attribute is a link to download a ZIP archive of PO files for the current project version;
    
    ``projectversion_set`` urls use the version ID (pk), not the slug or version name.
    
    This view is a "Retrieve and update" view, so you can see and get project details but also update its content.
    """
    serializer_class = ProjectCurrentSerializer
    model = Project
    
    def get_object(self):
        try:
            return Project.objects.get(slug=self.kwargs['slug'])
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        self.object = self.get_object()
        self.project_version = self.get_project_version()
        serializer = ProjectCurrentSerializer(self.object, context={'request': request})
        return Response(serializer.data)

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.object, version=self.kwargs['version'])
        return self.object.get_current_version()

    #def post(self, request, format=None):
        #serializer = ProjectCurrentSerializer(data=request.DATA, context={'request': request})
        #if serializer.is_valid():
            #serializer.save()
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectVersionDetail(APIView):
    """
    Retrieve a project version instance from its ID.
    
    Project version are freezed, so you can't update them.
    """
    def get_object(self, pk):
        try:
            return get_object_or_404(ProjectVersion, pk=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        self.project_version = self.get_object(pk)
        self.object = self.project_version.project
        serializer = ProjectVersionSerializer(self.object, context={'request': request})
        return Response(serializer.data)

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.object, version=self.kwargs['version'])
        return self.object.get_current_version()


class ProjectArchive(DownloadMixin, APIView):
    """
    Send a ZIP archive for the project's PO files
    
    TODO: share code from a mixin using code from ProjectExportView
    """
    content_type = 'application/x-gzip'
    filename_format = "{project_slug}_{timestamp}.tar.gz"
    
    def get_object(self, slug):
        try:
            return Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        self.object = self.get_object(slug)
        self.project_version = self.get_project_version()
        return super(ProjectArchive, self).get(request)

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.object, version=self.kwargs['version'])
        return self.object.get_current_version()

    def get_catalog_kind(self):
        kind = self.request.GET.get('kind', settings.DEFAULT_CATALOG_FILENAMES)
        if kind not in settings.AVAILABLE_CATALOG_FILENAMES:
            return settings.DEFAULT_CATALOG_FILENAMES
        return kind

    def get_context_data(self, **kwargs):
        context = super(ProjectArchive, self).get_context_data(**kwargs)
        context.update({
            'project': self.object,
            'project_slug': self.object.slug,
            'timestamp': self.get_filename_timestamp(),
        })
        return context
    
    def get_filename(self, context):
        return self.filename_format.format(**context)
    
    def get_content(self, context):
        archive_file = StringIO()
        
        po_project_export(self.object, self.project_version, archive_file, catalog_filename=self.get_catalog_kind())
        
        return archive_file.getvalue()
