#################
Using Aldryn Jobs
#################

.. note::
   This part of the guide assumes that django CMS has been :doc:`appropriately installed and
   configured </introduction/installation>`, including Aldryn Jobs, and that :doc:`a Jobs page
   has been set up </introduction/basic_usage>`.


*************
Add a vacancy
*************

Visit the Jobs page. You should see that the django CMS toolbar now contains a new item, *Jobs*. Select *Add Vacancy...* from this menu.

Provide some basic details, such as:

* the ``Lead in`` is a brief summary of the vacancy, that will be used in lists of vacancies, such
  as on a jobs landing page
* a ``Category``

and **Save** it.

It now exists in the database and will be listed on the Jobs page.

You can use the standard django CMS placeholder interface to add more content to your vacancies.


*******
Plugins
*******

The Jobs page is the easy way in to vacancies on the system, but Aldryn Jobs also includes a
number of plugins that can be inserted into any django CMS page - indeed, into any content - to
deliver information about jobs.

For example, if you have a news article announcing a new project, you can drop a Jobs
plugin into that page to display related vacancies.

List
====

Choose the vacancies you wish to have displayed.

Form for newsletter
===================

Surely we should get rid of this.

Categories list
=======================

A list of categories. Meh. If we're going to move from the
