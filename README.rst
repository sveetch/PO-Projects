**PO Projects** is a first attempt to build a PO file management factory, 
somehow like Transifex, but more simplest.

Principle is to have a frontend board to create new PO project from a POT file to import, 
then add it and manage language translation and finally export all these PO to include it 
in your app (django or another).

**This is in alpha staging, models have just been created and are not stable yet, there is no documentation and frontend is far from e usable, you've be warned!**

Actually we have
================

* View to create new project from a PO/POT file;
* View to create new project catalog;
* View to edit project catalog;
* View to update project catalogs from a template catalog (*.POT);

For beta staging this should implement
======================================

* Frontend to edit translation strings with Codemirror;
* Frontend to export project translations as PO files;
* Better model admin;
* Permission restriction;
* User authoring to know who has done what;

And some ideas for future
=========================

* External API access (restricted) to get PO files from external tools (like 
  Optimus or a Django app from an external site) ?
* Versioning ?
