"""
Some helpers to generate project, template message or catalogs
"""
import json

from po_projects.models import TemplateMsg, TranslationMsg
from po_projects.utils import get_message_strings


def create_templatemsgs(project_version, pot_catalog, commit=True):
    """
    Create template messages from a POT catalog
    
    @project_version: ProjectVersion instance
    @pot_catalog: Babel Catalog instance
    """
    entries = []
    # Walk in POT msg items to a template msg with its content
    for message in pot_catalog:
        if message.id:
            msgid, msgid_plural = get_message_strings(message.id)
                
            #print msgid
            #print "* python_format:", message.python_format
            #print "* pluralizable:", message.pluralizable
            #if msgid_plural: print "  - msgid_plural:", msgid_plural
            #print
            
            # Dump locations string into a JSON
            locations = json.dumps(message.locations)
            
            # Add template row from Catalog's message row
            entries.append( TemplateMsg(
                project_version=project_version,
                message=msgid,
                plural_message=msgid_plural,
                locations=locations,
                pluralizable=message.pluralizable,
                python_format=message.python_format,
            ) )
        
    if commit:
        TemplateMsg.objects.bulk_create(entries)
        
    return entries



def create_new_version(project, version, uploaded_catalog):
    """
    Open a new version for a project and fill it with datas from the given 
    POT file
    
    @project: Project instance
    @version: Version label as a string
    @uploaded_catalog: Babel Catalog instance
    """
    project_version = project.projectversion_set.create(
        version = version,
        header_comment = uploaded_catalog.header_comment,
        mime_headers = json.dumps(dict(uploaded_catalog.mime_headers)),
    )
    create_templatemsgs(project_version, uploaded_catalog)
    
    return project_version



def update_catalogs(project, previous_version, current_version):
    """
    Recreate all existing catalogs from previous project version in the new 
    current project, then update them from the given POT file
    
    Open the POT catalog, then merge translations from previous catalog 
    in the POT to result into a new up-to-date Catalog.
    
    @project: Project instance
    @previous_version: ProjectVersion instance for the previous version
    @current_version: ProjectVersion instance for the newly created version
    """
    # POT from current version
    current_template = current_version.get_babel_template()
    current_templatemsg_map = dict([(item.message, item) for item in current_version.templatemsg_set.all()])
    
    # For each existing catalog in previous project version
    for previous_catalog in previous_version.catalog_set.all():
        # Update previous catalog from the given POT file
        current_babel_catalog = previous_catalog.get_babel_catalog()
        current_babel_catalog.update(current_template)
        
        # Open a new catalog for current version where up-to-date translations 
        # will be created
        current_catalog = current_version.catalog_set.create(
            locale = previous_catalog.locale,
            header_comment = current_version.header_comment,
            mime_headers = current_version.mime_headers,
        )
        
        # Merge previous translations into template items
        entries = []
        for template_id,template_instance in current_templatemsg_map.items():
            # Defaults
            message = plural_message = ''
            fuzzy = pluralizable = python_format = False
            
            # If template row effectively exists into current PO catalog
            if template_id in current_babel_catalog:
                if current_babel_catalog[template_id].string:
                    message = current_babel_catalog[template_id].string
                    message, plural_message = get_message_strings(message)
                    
                fuzzy = current_babel_catalog[template_id].fuzzy
                pluralizable = current_babel_catalog[template_id].pluralizable
                python_format = current_babel_catalog[template_id].python_format
            
            # Message row related to the current catalog
            entries.append( TranslationMsg(
                template=template_instance,
                catalog=current_catalog,
                message=message,
                plural_message=plural_message,
                fuzzy=fuzzy,
                pluralizable=pluralizable,
                python_format=python_format,
            ) )
        
        # Bulk saving entries
        TranslationMsg.objects.bulk_create(entries)
