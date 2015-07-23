#################
Using Aldryn Jobs
#################

.. note::
   This part of the guide assumes that django CMS has been :doc:`appropriately installed and
   configured </introduction/installation>`, including Aldryn Jobs, and that :doc:`a Jobs page
   has been set up </introduction/basic_usage>`.


*****************
Add a job opening
*****************

Visit the Jobs page. You should see that the django CMS toolbar now contains a new item, *Jobs*.
Select *Add Job Opening...* from this menu.

Provide some basic details, such as:

* ``Short description``, a brief summary of the opening, that will be used in lists of openings,
  such as on a jobs landing page
* a ``Category``, required to associate job openings with supervisors, so you will need to create a
  ``Category`` too

and **Save** it.

It now exists in the database and will be listed on the Jobs page.

You can use the standard django CMS placeholder interface to add more content to your job openings.


*******
Plugins
*******

The Jobs page is the easy way in to job openings on the system, but Aldryn Jobs also includes a
number of plugins that can be inserted into any django CMS page - indeed, into any content - to
deliver information about jobs.

For example, if you have a news article announcing a new project, you can drop a Jobs
plugin into that page to display related job openings.

List
====

Choose the job openings you wish to have displayed.

Categories list
===============

Displays a list of categories of job openings.
