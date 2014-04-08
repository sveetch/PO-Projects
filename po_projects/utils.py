import json

from po_projects.models import TemplateMsg, TranslationMsg

def create_templatemsgs(project_version, pot_catalog, commit=True):
    """
    Create template messages from a POT catalog
    
    @project_version: ProjectVersion instance
    @pot_catalog: Babel Catalog instance
    """
    entries = []
    for message in pot_catalog:
        if message.id:
            #print message.id
            flags = json.dumps(list(message.flags))
            locations = json.dumps(message.locations)
            entries.append(TemplateMsg(project_version=project_version, message=message.id, locations=locations, flags=flags))
        
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
    Recreate all existing catalogs from previous version in the current one, 
    then update them from the given POT file
    
    @project: Project instance
    @previous_version: ProjectVersion instance for the previous version
    @current_version: ProjectVersion instance for the newly created version
    """
    current_template = current_version.get_babel_template()
    current_templatemsg_map = dict([(item.message, item) for item in current_version.templatemsg_set.all()])
    
    # For each existing catalog in previous project version
    for previous_catalog in previous_version.catalog_set.all():
        # Update previous catalog from the given POT file
        current_babel_catalog = previous_catalog.get_babel_catalog()
        current_babel_catalog.update(current_template)
        
        # New catalog for current version
        current_catalog = current_version.catalog_set.create(
            locale = previous_catalog.locale,
            header_comment = current_version.header_comment,
            mime_headers = current_version.mime_headers,
        )
        
        # Add entries to the new catalog from template messages
        entries = []
        for template_id,template_instance in current_templatemsg_map.items():
            message = ''
            fuzzy = False
            if template_id in current_babel_catalog:
                if current_babel_catalog[template_id].string:
                    message = current_babel_catalog[template_id].string
                fuzzy = current_babel_catalog[template_id].fuzzy
            entries.append(TranslationMsg(template=template_instance, catalog=current_catalog, message=message, fuzzy=fuzzy))
        
        # Bulk saving entries
        TranslationMsg.objects.bulk_create(entries)
