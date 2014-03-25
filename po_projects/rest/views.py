from cStringIO import StringIO

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, generics, renderers
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

from po_projects.models import Project, ProjectVersion, TemplateMsg, Catalog, TranslationMsg
from po_projects.rest.serializers import ProjectSerializer
from po_projects.utils import DownloadMixin
from po_projects.dump import po_project_export

@api_view(('GET',))
def api_root(request, format=None):
    """
    API Root is the entry point that display available endpoints
    """
    return Response({
        'projects': reverse('po_projects:api-project-list', request=request, format=format)
    })


class ProjectList(APIView):
    """
    List all projects
    """
    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data)


class ProjectDetail(APIView):
    """
    Retrieve a project instance from its slug
    """
    def get_object(self, slug):
        try:
            return Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        self.object = self.get_object(slug)
        self.project_version = self.get_project_version()
        serializer = ProjectSerializer(self.object)
        return Response(serializer.data)

    def get_project_version(self):
        if "version" in self.kwargs:
            return get_object_or_404(ProjectVersion, project=self.object, version=self.kwargs['version'])
        return self.object.get_current_version()

    #def post(self, request, format=None):
        #serializer = ProjectSerializer(data=request.DATA)
        #if serializer.is_valid():
            #serializer.save()
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectArchive(DownloadMixin, APIView):
    """
    Send project archive
    
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
