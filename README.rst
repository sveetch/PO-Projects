**PO Projects** is a first attempt to build a PO file management factory like, 
somehow like Transifex, but more simplest.

Principle is to have a frontend board to create new PO project from a POT file to import, 
then add it and manage language translation and finally export all these PO to include it 
in your app (django or another).

**This is in alpha staging, models are not stable yet, there is no documentation and frontend is far from usable, you've be warned!**

Actually we have
================

* View to create new project from a PO/POT file;
* View to create new project translation and edit them;
* View to export project translations as PO files;
* View to export an archive (zip/tarball) of all translations as PO files from a project;

For beta staging this should implement
======================================

* Rich editor usage (with colored syntax) on text edit;
* Better model admin;
* Permission restriction;
* User authoring to know who has done what;
* External API access to get PO files or global project archive from external tools 
  (like Optimus or a Django app from an external site) ?
* Restrict external API access
