**PO Projects** is a first attempt to build a PO file management factory like, 
somehow like Transifex, but more simplest.

Principle is to have a frontend board to create new PO project from a POT file to import, 
then add it and manage language translation and finally export all these PO to include it 
in your app (django or another).

**This is in beta staging, models are not stable yet, there is no documentation and frontend is far from usable, you've be warned!**

Actually we have
================

* View to create new project from a PO/POT file;
* View to create new project translation and edit them;
* View to export project translations as PO files;
* View to export an archive (zip/tarball) of all translations as PO files from a project;
* Manage fuzzy mode for translations;

For beta staging this should implement
======================================

* Form to import a catalog (PO) to update a catalog;
* Better global ergonomy;
* Better model admin;
* Permission restriction;
* User authoring to know who has done what;
* External API access to get PO files or global project archive from external tools 
  (like Optimus or a Django app from an external site) ?
* Restrict external API access

External API access
===================

We should need of two clients : 

* One for Django webapp, shipped as a Django app that only exposes a command line tool, no needs of model;
* One for Optimus, allready shipped as a new command line tool;

The access to the API need to be protected and restricted to avoid that anyone can download and/or edit project translations.

API actions should be :

* Export project, this will send a tarball containing the locale directory to overwrite the one in the destination project (in the django or optimus project, not the translation project stored in Po-Projects);
* Receiving new POT file to update a project template and catalogs;

