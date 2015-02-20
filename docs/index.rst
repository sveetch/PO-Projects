.. PO-Projects documentation master file, created by
   sphinx-quickstart on Fri Feb 20 02:16:37 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _Django: https://www.djangoproject.com/
.. _South: http://south.readthedocs.org/en/latest/
.. _autobreadcrumbs: https://github.com/sveetch/autobreadcrumbs
.. _django-crispy-forms: https://github.com/maraujop/django-crispy-forms
.. _djangorestframework: http://www.django-rest-framework.org
.. _PO-Projects-client: https://github.com/sveetch/PO-Projects-client

Welcome to PO-Projects's documentation!
=======================================

**PO Projects** is a PO file management factory.

Goal
****

Have a clean and ergonomic frontend to manage PO files for webapp projects and enable a REST API to deploy PO files into webapp projects.

Features
********

* View to create new project from a PO/POT file;
* View to create new project translation and edit them;
* View to export project translations as PO files;
* View to export an archive (zip/tarball) of all translations as PO files (and their compiled MO files) from a project;
* Manage fuzzy mode for translations;
* Form to import a catalog (PO) to update a catalog;
* Nice frontend with Foundation;
* Permission restriction;
* Restricted API access with `djangorestframework`_ to get PO files or global project 
  archive from external tools (like Optimus or a Django app from an external site) ?

Links
*****

* Read the documentation on `Read the docs <https://po-projects.readthedocs.org/>`_;
* Download his `PyPi package <http://pypi.python.org/pypi/PO-Projects>`_;
* Clone it on his `Github repository <https://github.com/sveetch/PO-Projects>`_;

Table of contents
*****************

.. toctree::
   :maxdepth: 2
   
   install.rst
   usage.rst
   changelog.rst
