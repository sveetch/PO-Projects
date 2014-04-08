import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404

class DownloadMixin(object):
    """
    Simple Mixin to send a downloadable content
    
    Inherits must have :
    
    * Filled the ``self.content_type`` attribute with the content content_type to send;
    * Implementation of ``get_filename()`` that return the filename to use in response 
      headers;
    * Implementation of ``get_content()`` that return the content to send as downloadable.
    
    If the content is a not a string, it is assumed to be a fileobject to send as 
    the content with its ``read()`` method.
    
    Optionnaly implement a ``close_content()`` to close specifics objects linked to 
    content fileobject, if it does not exists a try will be made on a close() method 
    on the content fileobject;
    
    A "get_filename_timestamp" method is implemented to return a timestamp to use in your 
    filename if needed, his date format is defined in "timestamp_format" attribute (in a 
    suitable way to use with strftime on a datetime object).
    """
    content_type = None
    timestamp_format = "%Y-%m-%d"
    
    def get_filename_timestamp(self):
        return datetime.datetime.now().strftime(self.timestamp_format)
    
    def get_filename(self, context):
        raise ImproperlyConfigured("DownloadMixin requires an implementation of 'get_filename()' to return the filename to use in headers")
    
    def get_content(self, context):
        raise ImproperlyConfigured("DownloadMixin requires an implementation of 'get_content()' to return the downloadable content")
    
    def render_to_response(self, context, **response_kwargs):
        if getattr(self, 'content_type', None) is None:
            raise ImproperlyConfigured("DownloadMixin requires a definition of 'content_type' attribute")
        # Needed headers
        response = HttpResponse(content_type=self.content_type, **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(self.get_filename(context))
        # Read the content file object or string, append it to response and close it
        content = self.get_content(context)
        if isinstance(content, basestring):
            response.write(content)
        else:
            response.write(content.read())
        # Conditionnal closing content object
        if hasattr(self, 'close_content'):
            self.close_content(context, content)
        elif hasattr(content, 'close'):
            content.close()
            
        return response

    def get_context_data(self, **kwargs):
        return {
            'params': kwargs
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
