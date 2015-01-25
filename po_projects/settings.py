# -*- coding: utf-8 -*-
"""
Default settings
"""

# Used to build path and file names in exported tarball archives for projects
POT_ARCHIVE_PATH = "locale/{catalog_filename}.pot"
PO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/{catalog_filename}.po"
MO_ARCHIVE_PATH = "locale/{locale}/LC_MESSAGES/{catalog_filename}.mo"

# Available PO filename types
DEFAULT_CATALOG_FILENAMES = 'messages'
AVAILABLE_CATALOG_FILENAMES = ('django', 'messages')