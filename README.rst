**PO Projects** is a first attempt to build a PO file management factory, 
somehow like Transifex, but more simplest.

Principle is to have a frontend board to create new translation project from a 
POT file to import, manage translation catalogs (for languages) and finally 
export all these PO to include them in your app (django or another).

**This is in alpha staging, models have just been created and are not stable yet, there is no documentation and frontend is far from e usable, you've be warned!**

Actually we have
================

* View to create new project from a PO/POT file;
* View to create new project catalog;
* View to edit project catalog messages;
* View to update project catalogs from a template catalog (*.POT);

For beta staging this should implement
======================================

* Frontend to export project translations as PO files;
* Better model admin;
* Permission restriction;
* Better frontend ergonomy and look;
* Better mime type management in generated PO files;

And some ideas for future
=========================

* External API access (restricted) to get PO files from external tools (like 
  Optimus or a Django app from an external site) ?
* Versioning ?
