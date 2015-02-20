.. _Django: https://www.djangoproject.com/
.. _djangorestframework: http://www.django-rest-framework.org
.. _PO-Projects-client: https://github.com/sveetch/PO-Projects-client

=====
Usage
=====

Introducing to PO
*****************

PO file (``messages.po``) is a **gettext** format in plain text to manage texts translation management.

A PO file contains translations referenced with an identifiant (``msgid``) that is the text source marked for translation. 

For each identifiant there is one message translation (``msgstr``) that should contain the translation of the text source. If the translation is empty, it is ignored and the text source will be used instead.

Also a translation can be marked as **fuzzy**, that means gettext has finded a translation has changed (its id or its message) but it is not sure about it. Until the *fuzzy* mark is keeped, the translation will be ignored, you have to remove it the translation message is right.

When a PO file is finished, a developer deploy it with compiling it to a MO file (``messages.mo``) that is ready to use by an application.

Workflow
********

Previously, translators and developers have to share PO files, deploy them and compile them manually.

With *PO-Projects* this is more simple if `PO-Projects-client`_ is installed and configured for the translation project.

Pushing new extracted translation
---------------------------------

#. When templates or code has changed, developers extract again translation into the PO files;
#. Developers go into the webapp project and use the client's ``push``;
#. It's done, new and updated translations sources are sended to the  factory, the translators can work on them;

Pulling translation from the factory
------------------------------------

#. Translators do translations onto a project;
#. When they have finished they ask a developer to deploy PO files;
#. Developers go into the webapp project and use the client's ``pull`` command (then restart the webserver if any);
#. It's done
