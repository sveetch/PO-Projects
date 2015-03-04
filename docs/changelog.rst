Changelog
=========

Version 0.8.0 - 04 March 2015
-----------------------------

* Add ``pluralizable`` and ``python_format`` attributes to ``TemplateMsg`` model and fill them from messages flags;
* Remove ``flags`` attributes from ``TemplateMsg`` model, now the flags are computed from model attributes (``python_format``);
* Add ``plural_message`` attributes to ``TranslationMsg`` model filled when there is plural translation;
* Update core to rightly use these new attributes (when creating/updating catalog);
* Change catalog's translation form to fit with plural messages;
* Add new south migrations for theses changes;

Version 0.7.4 - 20 February 2015
--------------------------------

* Add forgotten locale directory;
* Fix bug on compiled PO in project's tarball archive so the client deploys correct PO and MO files;
* Starting new documentation;

Version 0.7.3 - 19 February 2015
--------------------------------

* Better layout and ergonomy on all ressources;

Version 0.7.2 - 16 February 2015
--------------------------------

* Better Catalog create form on project details page;

Version 0.7.1 - 16 February 2015
--------------------------------

* Better translation source rendering in the translation update form;
* Remove the Project's slug field from the project update form;

Version 0.7.0 - 15 February 2015
--------------------------------

* Add a more ergonomic interface for translation form with sticky fixed menu, translation statistics and a more readable layout;
* Add 'domain' attribut on Project model so now projects have an explicit domain name to use for write PO catalog files;
* Force gettext domain in forget Babel catalogs;
* Move forms and add crispies;
* Add assets for django-asets;
* Add Compass stuff to build SCSS;
* Add static files;
