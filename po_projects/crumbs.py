from autobreadcrumbs import site
from django.utils.translation import ugettext_lazy

site.update({
    'project-index': ugettext_lazy('PO Projects'),
    'project-create': ugettext_lazy('Create a new project'),
    'project-details': ugettext_lazy('{% load i18n %}<small>{% trans "Project" %}</small> {{ project.name }}'),
    'project-update': ugettext_lazy('Project update'),
    'project-download': None,
    'catalog-details': ugettext_lazy('{% load i18n %}<small>{% trans "Catalog" %}</small> {{ catalog.get_locale_name }}'),
    'catalog-messages-edit': ugettext_lazy('Edit messages'),
    'catalog-messages-download': None,
})