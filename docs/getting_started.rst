===============
Getting Started
===============

Welcome to Django Palette! This guide will help you get up and running quickly.

What is Django Palette?
=======================

Django Palette is a Django package that enhances the admin interface with:

- Modern Bootstrap 5 styling
- Responsive, mobile-friendly design
- Reusable component-based templating
- Custom template tags for building UI
- Beautiful pre-styled admin pages
- Grid/list view toggles for model lists
- Drag-and-drop file upload with preview

Who is it for?
==============

Django Palette is for Django developers who want to:

- Create beautiful, modern admin interfaces quickly
- Build reusable UI components
- Use a familiar template tag syntax
- Maintain full Django admin functionality
- Customize the look and feel without losing power

Next Steps
==========

Ready to get started? Check out:

1. :doc:`installation` - Install django-palette
2. :doc:`quick_start` - Get it working in 5 minutes
3. :doc:`features` - Explore all features
4. :doc:`template_tags` - Learn the custom template tags
5. :doc:`components` - Build custom components

Key Concepts
============

Components
----------

Components are reusable UI elements defined with the ``palette_component`` tag. They can have multiple named blocks that can be overridden.

Blocks
------

Blocks (``palette_block``) are named areas within a component that can be overridden when the component is rendered.

Overrides
---------

Overrides (``palette_override``) replace the content of a specific block when rendering a component.

Template Tags
-------------

Custom Django template tags (``palette_component``, ``palette_ui``, ``palette_block``, ``palette_override``) for building dynamic admin interfaces.

Features Highlights
===================

Modern Admin Interface
~~~~~~~~~~~~~~~~~~~~~~

All admin pages are styled with Bootstrap 5, featuring:

- Clean, professional design
- Responsive layouts for all devices
- Consistent color scheme
- Professional gradients and shadows

Sidebar Navigation
~~~~~~~~~~~~~~~~~~~

A collapsible sidebar showing:

- Navigation to apps and models
- Quick add buttons for each model
- Mobile-friendly toggle

Component System
~~~~~~~~~~~~~~~~

Build components once, use them anywhere:

- Define with ``palette_component``
- Render with ``palette_ui``
- Override blocks with ``palette_override``
- Pass context variables naturally

Beautiful Templates
~~~~~~~~~~~~~~~~~~~

Includes pre-built templates for:

- Dashboard/index page
- Model change list (with grid/list toggle)
- Add/edit forms (with file upload)
- Login page
- Password change
- Delete confirmation

Need Help?
==========

- Read :doc:`quick_start` for a 5-minute setup
- Check :doc:`template_tags` for tag documentation
- See :doc:`examples` for code examples
- Open an issue on `GitHub <https://github.com/ogofe/django-palette/issues>`_
