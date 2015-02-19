# -*- coding: utf-8 -*-
"""
Default settings
"""
gettext = lambda s: s

# Used to build path and file names in exported tarball archives for projects
POT_ARCHIVE_PATH = "locale/{catalog_filename}.pot"
PO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/{catalog_filename}.po"
MO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/{catalog_filename}.mo"

# Available PO's translations domain names
GETTEXT_DOMAINS = (
    ('messages', gettext('Default gettext\'s domain')),
    ('django', gettext('Django\'s domain')),
)
DEFAULT_GETTEXT_DOMAINS = 'django'
