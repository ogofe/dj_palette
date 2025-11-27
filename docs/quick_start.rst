===========
Quick Start
===========

Get django-palette running in 5 minutes!

Installation (1 minute)
=======================

1. Install the package:

.. code-block:: bash

   pip install dj-palette

2. Add to ``settings.py``:

.. code-block:: python

   INSTALLED_APPS = [
       'dj_palette',
       'dj_palette.palette_admin', # optional, only if you want the best looking admin UI
       'django.contrib.admin',
       # ... rest of your apps
   ]

3. Run migrations:

.. code-block:: bash

   python manage.py migrate

4. Collect static files:

.. code-block:: bash

   python manage.py collectstatic

5. Start the server:

.. code-block:: bash

   python manage.py runserver

Visit http://localhost:8000/admin/ and you'll see the beautiful django-palette admin interface!

Creating a Component (2 minutes)
================================

Create a file ``templates/components/stat_card.html``:

.. code-block:: django

   {% load palette %}

   {% palette_component "stat_card" %}
     <div class="card border-0 shadow-sm">
       <div class="card-body text-center">
         {% palette_block "stat_content" %}
           <h2 class="display-4 text-primary">{{ number }}</h2>
           <p class="text-muted">{{ label }}</p>
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

Using the Component (2 minutes)
================================

In your template (e.g., ``templates/admin/index.html``):

.. code-block:: django

   {% load palette %}

   <div class="row">
     <div class="col-md-4">
       {% palette_ui "stat_card" with number="1,234" label="Total Users" %} {% endpalette_ui %}
     </div>
     
     <div class="col-md-4">
       {% palette_ui "stat_card" with number="89" label="Active Today" %}
         {% palette_override "stat_content" %}
           <h2 class="display-4 text-success">{{ number }}</h2>
           <p class="text-muted">{{ label }}</p>
           <small>Updated just now</small>
         {% endpalette_override %}
       {% endpalette_ui %}
     </div>
   </div>

That's it! You now have:

✅ A beautiful admin interface
✅ A reusable component
✅ The ability to customize components with overrides

What's Next?
============

Learn More
~~~~~~~~~~

- :doc:`features` - Explore all features
- :doc:`template_tags` - Learn all template tags
- :doc:`components` - Build more complex components
- :doc:`examples` - See more examples

Customize Further
~~~~~~~~~~~~~~~~~~

- Override admin templates in your project's ``templates/admin/`` directory
- Create more components in ``templates/components/`` or ``<your_app>/templates/<your_app>/components/`` (always use named subfolders when going with in-app templates approach)
- Use the filters: ``admin_fields`` and ``admin_field``

Need Help?
~~~~~~~~~~

- Check the :doc:`features` page for more information
- Read the full :doc:`template_tags` documentation
- See :doc:`examples` for more code examples
- Open an issue on `GitHub <https://github.com/ogofe/django-palette/issues>`_

Key Concepts
============

**Components**: Reusable UI elements defined with ``palette_component``

**Blocks**: Named areas within components that can be overridden with ``palette_override``

**Rendering**: Use ``palette_ui`` to render a component with context variables

**Customization**: Override blocks without redefining entire components

Example: Creating a Dashboard
==============================

Create ``templates/admin/index.html``:

.. code-block:: django

   {% extends "admin/base_site.html" %}
   {% load palette %}

   {% block content %}
     <div class="container-fluid">
       <h1>Dashboard</h1>
       
       <div class="row mt-4">
         <div class="col-md-4">
           {% palette_ui "stat_card" with number="1,234" label="Total Users" %}{% endpalette_ui %}
         </div>
         <div class="col-md-4">
           {% palette_ui "stat_card" with number="456" label="Active Sessions" %}{% endpalette_ui %}
         </div>
         <div class="col-md-4">
           {% palette_ui "stat_card" with number="789" label="Total Orders" %}{% endpalette_ui %}
         </div>
       </div>
     </div>
   {% endblock %}

This creates a beautiful dashboard with three stat cards!

Ready?
======

Start building! Check out :doc:`examples` for more ideas.
