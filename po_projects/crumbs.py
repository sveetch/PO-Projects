from autobreadcrumbs import site
from django.utils.translation import ugettext_lazy

site.update({
    'po_projects:project-index': ugettext_lazy('PO Projects'),
    'po_projects:project-create': ugettext_lazy('Create a new project'),
    'po_projects:project-details': ugettext_lazy('<small class="subhead">Project</small> {{ project.name }}'),
    'po_projects:project-update': ugettext_lazy('Settings'),
    'po_projects:project-download': None,
    'po_projects:catalog-details': ugettext_lazy('<small class="subhead">Catalog</small> {{ catalog.get_locale_name }}'),
    'po_projects:catalog-messages-edit': ugettext_lazy('Edit messages'),
    'po_projects:catalog-messages-download': None,
})