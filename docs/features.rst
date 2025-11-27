========
Features
========

Django Palette comes with a comprehensive set of features designed to make building beautiful admin interfaces easy and enjoyable.

Beautiful Bootstrap Admin Interface
===================================

Out of the box, django-palette replaces Django's default admin interface with a modern, responsive Bootstrap 5 design.

**What you get:**

- Clean, professional design with consistent styling
- Beautiful color scheme with professional gradients and shadows
- Responsive layouts that work on desktop, tablet, and mobile
- Smooth transitions and animations
- Bootstrap Icons integration
- Accessible HTML with proper semantic markup

**Included Templates:**

- ``base_site.html`` - Main admin layout with sidebar
- ``index.html`` - Dashboard/home page
- ``change_list.html`` - Model list view with grid/list toggle
- ``change_form.html`` - Add/edit form with file upload
- ``change_password.html`` - Password change form
- ``delete_confirmation.html`` - Delete confirmation dialog
- ``login.html`` - Login page with gradient design

Responsive Design
=================

Everything is built to work on any device size.

**Desktop Experience:**

- Full sidebar navigation always visible
- Multi-column layouts
- Hover effects on interactive elements
- Full feature access

**Mobile Experience:**

- Collapsible sidebar with toggle button
- Single-column layouts
- Touch-friendly buttons and controls
- All features accessible

Reusable Components
===================

Build UI components once and reuse them throughout your admin interface.

**Component Features:**

- Define with ``palette_component`` template tag
- Render with ``palette_ui`` template tag
- Pass context variables naturally
- Override specific blocks with ``palette_override``
- No repetition of template code
- Clean separation of concerns

**Example:**

.. code-block:: django

   {% palette_component "card" %}
     <div class="card">
       {% palette_block "content" %}
         <p>Default content</p>
       {% endpalette_block %}
     </div>
   {% endpalette_component %}

Then use it anywhere:

.. code-block:: django

   {% palette_ui "card" with title="My Card" %}

Component Slots and Overrides
=============================

Extend components without modifying them using blocks and overrides.

**Named Blocks:**

Define named areas in components that can be customized:

.. code-block:: django

   {% palette_block "header" %}
     <h1>{{ title }}</h1>
   {% endpalette_block %}

**Overrides:**

Replace blocks when rendering:

.. code-block:: django

   {% palette_ui "card" %}
     {% palette_override "header" %}
       <h1 class="text-primary">Custom Title</h1>
     {% endpalette_override %}
   {% endpalette_ui %}

Template Tags
=============

Custom Django template tags for building dynamic admin interfaces.

**Available Tags:**

- ``palette_component`` - Define a reusable component
- ``palette_block`` - Define an overridable block within a component
- ``palette_ui`` - Render a component with props
- ``palette_override`` - Override a block when rendering

See :doc:`template_tags` for detailed documentation.

Enhanced Admin Pages
====================

All admin pages are beautifully styled and enhanced with modern UX patterns.

**Change List Page:**

- Grid view: Responsive card layout
- List view: Bootstrap table with hover effects
- View toggle: Switch between grid/list (localStorage persistence)
- Actions bar: Styled form for bulk actions
- Search and filtering
- Pagination

**Change Form Page:**

- Responsive field layout
- File upload with drag-and-drop
- Image preview for uploads
- Inline related objects
- Error highlighting
- Sticky action bar

**Login Page:**

- Full-screen gradient background
- Centered card layout
- Modern form styling
- Accessible form controls

**Password Change:**

- Clean form layout
- Password strength feedback
- Clear instructions

Django Admin Integration
========================

Full compatibility with Django's admin system means you don't lose any power.

**What Works:**

- Django permissions system
- Model admin customization
- Inline relationships
- Custom actions
- Filters and search
- All admin options

No migration needed - django-palette works alongside your existing admin setup.

Sidebar Navigation
===================

An intelligent sidebar showing your app and model structure.

**Features:**

- Organized by app
- Quick "Add" buttons for each model
- Active state highlighting
- Collapsible on mobile
- Smooth toggle animation
- Search through apps and models

Drag-and-Drop File Upload
=========================

Modern file upload interface in forms.

**Features:**

- Drag files directly onto the zone
- Click to browse and select files
- Image preview for image files
- File icon for non-image files
- Responsive grid preview
- Works with all file types

Grid/List Toggle Views
======================

Multiple ways to view your model lists.

**Grid View:**

- Beautiful card-based layout
- Responsive auto-fill grid
- Shows key information at a glance
- Great for visual content

**List View:**

- Traditional table layout
- Hover effects
- Easy scanning of data
- Familiar to Django users

**Toggle:**

- Easy switching with buttons
- Preference saved in localStorage
- Persists across sessions
- No server-side storage needed

Built-in Filters
================

Helper filters for common admin tasks.

**admin_fields Filter:**

Display all fields of an object:

.. code-block:: django

   {% for field_name, field_value in object|admin_fields %}
     <p>{{ field_name }}: {{ field_value }}</p>
   {% endfor %}

**admin_field Filter:**

Get a specific field:

.. code-block:: django

   {{ object|admin_field:"email" }}

Zero Breaking Changes
=====================

Works alongside existing Django admin - no migration pain.

**Compatible With:**

- Django 2.2+
- Python 3.7+
- All Django admin customizations
- Existing templates and static files
- Third-party admin packages

**Can be adopted gradually:**

- Use django-palette templates alongside Django defaults
- Override specific templates only
- Start with the admin interface, add custom pages later

Static Files Included
=====================

All necessary assets are included and automatically available.

**Included:**

- Bootstrap 5 CSS and JS
- Bootstrap Icons
- Custom admin styling
- HTMX for dynamic interactions
- Select2 for enhanced selects
- Responsive CSS Grid layouts
- Smooth animations and transitions

No external CDN dependencies needed - everything is bundled.

Customization
==============

Everything can be customized to match your brand.

**How to Customize:**

1. Override templates in your project's ``templates/admin/`` directory
2. Create custom components in ``templates/components/``
3. Add custom CSS in your static files
4. Use template variables to customize content

See :doc:`customization` for detailed instructions.
