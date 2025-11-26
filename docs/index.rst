====================
Django Palette Docs
====================

Welcome to Django Palette documentation!

**django-palette** is a powerful Django admin interface framework with beautiful Bootstrap styling, reusable components, and custom template tags for building elegant admin pages.

.. image:: ../logo.jpg
   :width: 300px
   :align: center

Table of Contents
==================

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started
   installation
   quick_start

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   features
   template_tags
   components
   admin_templates
   customization

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

.. toctree::
   :maxdepth: 2
   :caption: Contributing

   contributing
   changelog

Quick Links
===========

- `GitHub Repository <https://github.com/ogofe/django-palette>`_
- `PyPI Package <https://pypi.org/project/dj-palette/>`_
- `Issue Tracker <https://github.com/ogofe/django-palette/issues>`_

Features
========

- 🎨 **Beautiful Bootstrap Admin Interface** - Modern, responsive admin templates with Bootstrap 5 styling
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- 🧩 **Reusable Components** - Build custom UI components with the ``palette_component`` tag
- 🔄 **Component Slots** - Define and override content blocks within components using ``palette_block`` and ``palette_override``
- 🎯 **Template Tags** - Custom tags for rendering and managing components with context variables
- 📊 **Enhanced Admin Pages** - Pre-styled templates for change_list, change_form, login, password change, and delete confirmation
- 🔐 **Django Admin Integration** - Full compatibility with Django's permissions and admin system
- 📁 **Sidebar Navigation** - Collapsible sidebar with app and model navigation
- 🎨 **Drag-and-drop File Upload** - Modern file upload interface with image preview
- 🔍 **Grid/List Toggle Views** - Multiple view modes for displaying model lists
- ⚡ **Zero Breaking Changes** - Works alongside existing Django admin setup

Installation
============

Install django-palette using pip:

.. code-block:: bash

   pip install dj-palette

Then add it to your ``INSTALLED_APPS`` in settings.py:

.. code-block:: python

   INSTALLED_APPS = [
       'dj_palette',
       'dj_palette.palette_admin',
       'django.contrib.admin',
       ...
   ]

For detailed setup instructions, see :doc:`installation`.

Support
=======

- **Documentation**: https://django-palette.readthedocs.io
- **GitHub Issues**: https://github.com/ogofe/django-palette/issues
- **Email**: 7thogofe@gmail.com

License
=======

MIT License © 2025 Joel O. Tanko
