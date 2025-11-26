============
Installation
============

Installing django-palette is straightforward. Follow the steps below to get it working in your Django project.

Prerequisites
=============

- Python 3.7 or higher
- Django 2.2 or higher
- pip

Step 1: Install the Package
============================

Install django-palette using pip:

.. code-block:: bash

   pip install dj-palette

Step 2: Add to INSTALLED_APPS
=============================

In your Django project's ``settings.py``, add ``dj_palette`` and ``dj_palette.palette_admin`` to the ``INSTALLED_APPS`` list:

.. code-block:: python

   INSTALLED_APPS = [
       'dj_palette',  # Add this
       'dj_palette.palette_admin',  # Add this
       
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       
       # ... your other apps
   ]

The order matters - ``dj_palette`` should come before ``django.contrib.admin``.

Step 3: Configure URLs (Optional)
==================================

By default, django-palette works with the standard Django admin. If you want to use a custom admin site, you can configure it:

.. code-block:: python

   # urls.py
   from django.contrib import admin
   from django.urls import path

   urlpatterns = [
       path('admin/', admin.site.urls),
       # ... other patterns
   ]

Step 4: Run Migrations
======================

If you're using ``dj_palette.palette_admin``, run migrations to set up the necessary tables:

.. code-block:: bash

   python manage.py migrate

Step 5: Collect Static Files
=============================

Collect static files so Bootstrap, icons, and other assets are available:

.. code-block:: bash

   python manage.py collectstatic

This will copy all CSS, JS, and font files to your static files directory.

Step 6: Create a Superuser (if needed)
=======================================

If you haven't already, create a superuser account:

.. code-block:: bash

   python manage.py createsuperuser

Step 7: Test the Installation
==============================

Start your development server:

.. code-block:: bash

   python manage.py runserver

Visit http://localhost:8000/admin/ and log in with your superuser credentials. You should see the beautiful django-palette admin interface!

Troubleshooting
===============

Static Files Not Loading
~~~~~~~~~~~~~~~~~~~~~~~~

If CSS and JS aren't loading:

1. Make sure ``django.contrib.staticfiles`` is in ``INSTALLED_APPS``
2. Run ``python manage.py collectstatic`` again
3. Check that ``STATIC_URL`` is set in settings.py (default is ``/static/``)

Import Errors
~~~~~~~~~~~~~

If you get import errors:

1. Make sure ``dj_palette`` is in ``INSTALLED_APPS``
2. Verify the package was installed: ``pip show dj-palette``
3. Check that there are no circular imports in your settings

Templates Not Found
~~~~~~~~~~~~~~~~~~~

If admin templates aren't showing:

1. Ensure ``APP_DIRS`` is True in the TEMPLATES configuration (default is True)
2. Make sure ``dj_palette`` comes before ``django.contrib.admin`` in ``INSTALLED_APPS``

Upgrade from Previous Version
==============================

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade dj-palette

Then run migrations:

.. code-block:: bash

   python manage.py migrate

Next Steps
==========

Great! Now that django-palette is installed, check out:

- :doc:`quick_start` - Get it working in 5 minutes
- :doc:`features` - Explore all features
- :doc:`template_tags` - Learn the template tags
- :doc:`examples` - See code examples

Need Help?
==========

- Read the full documentation at https://django-palette.readthedocs.io
- Check the `GitHub README <https://github.com/ogofe/django-palette>`_
- Open an issue on `GitHub <https://github.com/ogofe/django-palette/issues>`_
