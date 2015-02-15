# -*- coding: utf-8 -*-
"""
Default settings
"""
# Used to build path and file names in exported tarball archives for projects
POT_ARCHIVE_PATH = "locale/{catalog_filename}.pot"
PO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/{catalog_filename}.po"
MO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/{catalog_filename}.mo"

# Available PO's translations domain names
GETTEXT_DOMAINS = (
    ('messages', 'Default gettext\'s domain'),
    ('django', 'Django\'s domain'),
)
DEFAULT_GETTEXT_DOMAINS = 'django'

# TODO:Old to remove
DEFAULT_CATALOG_FILENAMES = 'messages'
AVAILABLE_CATALOG_FILENAMES = ('django', 'messages')
