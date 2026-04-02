=============
Palette Admin
=============

The Palette Admin interface is a beautiful, modern replacement for Django's default admin interface.

Overview
========

``dj_palette.palette_admin`` provides an enhanced Django admin interface with:

- Modern Bootstrap 5 styling
- Responsive, mobile-friendly design
- Collapsible sidebar navigation
- Grid/list toggle for model lists
- Beautiful forms with drag-and-drop file upload
- Professional color scheme and typography
- Smooth animations and transitions

Installation
============

The admin interface is included with the ``dj_palette.palette_admin`` app.

**In settings.py:**

.. code-block:: python

   INSTALLED_APPS = [
       'dj_palette',
       'dj_palette.palette_admin',  # Add this
       'django.contrib.admin',
       # ... rest of apps
   ]

**In urls.py:**

.. code-block:: python

   from django.contrib import admin
   from django.urls import path

   urlpatterns = [
       path('admin/', admin.site.urls),
   ]

**Run migrations:**

.. code-block:: bash

   python manage.py migrate

**Collect static files:**

.. code-block:: bash

   python manage.py collectstatic

Admin Pages Included
====================

The following admin pages are beautifully styled:

Login Page (login.html)
~~~~~~~~~~~~~~~~~~~~~~~

- Full-screen gradient background
- Centered login card
- Username and password fields with icons
- Modern submit button
- Accessible form controls

**Customization:**

Override ``templates/admin/login.html`` in your project.

Change List Page (change_list.html)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Displays a list of model instances with multiple view options.

**Grid View:**

- Responsive card layout
- Displays key information at a glance
- Beautiful shadows and spacing
- Hover effects

**List View:**

- Traditional Bootstrap table
- Sortable columns
- Hover highlighting
- Familiar interface

**Features:**

- View toggle buttons (Grid/List)
- Search functionality
- Filter sidebar
- Bulk action form
- Pagination
- "Add" button
- Per-page limit selector

**Customization:**

Override ``templates/admin/change_list.html`` in your project.

Change Form Page (change_form.html)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beautiful form for creating and editing instances.

**Features:**

- Responsive field layout
- Grouped fieldsets with headers
- Drag-and-drop file upload with preview
- Image preview in fields
- Error highlighting with red borders
- Help text below fields
- Sticky action footer bar
- Save, Delete, and Save and Add Another buttons
- Support for inline related objects
- Password field rendered as read-only hash with a change-password link

**File Upload:**

The file input includes:

- Drag-and-drop zone
- Click to browse
- Image preview for image files
- File icon for other file types
- Responsive grid preview
- Works with any file type

**Related Object Modal Popup:**

ForeignKey and ManyToManyField selects that allow adding related objects show an
**Add** button beside the field. Clicking it opens a Bootstrap modal containing an
iframe loaded with the related model's add form — the user never leaves the current page.

How it works:

1. The **Add** button carries ``data-model-name``, ``data-app-label``, and
   ``data-field-id`` attributes identifying the target model and the parent select field.
2. The iframe loads ``/<admin-prefix>/<app>/<model>/add/?_to_field=id&_popup=1``.
3. When the form inside the iframe is saved successfully, Django injects a
   ``#django-admin-popup-response-constants`` element with the new object's PK and
   label as JSON.
4. The iframe's load event detects this element, reads the response, and calls
   ``window.parent.dismissAddRelatedModal(pk, label)``.
5. ``dismissAddRelatedModal`` appends the new option to the parent Select2 field,
   marks it as selected, and closes the modal.
6. If the iframe form has validation errors (no response constants found), the modal
   stays open so the user can correct them.

**Dark mode** is automatically propagated from the parent page into the iframe on load.

The modal is only shown for fields where ``can_add_related`` is ``True`` on the widget
(Django's default for ForeignKey/M2M fields where the user has ``add`` permission).

``popup_response.js``
^^^^^^^^^^^^^^^^^^^^^

``static/js/popup_response.js`` is loaded on every admin page and manages all
popup/iframe communication. It is compatible with both Palette Admin's iframe modal
and Django's traditional new-window popup system.

**Responsibilities:**

- Detects context: iframe vs. traditional popup window (``window.opener``).
- Reads ``?_popup=1``, ``?_to_field``, and ``?_popup_id`` URL parameters.
- Reads the saved object's PK and label from Django's
  ``#django-admin-popup-response-constants`` element.
- Routes the response to the correct handler:

  - **Iframe context** → calls ``window.parent.dismissAddRelatedModal(pk, label)``
    or falls back to ``postMessage``.
  - **Traditional popup** → calls ``window.opener.dismissAddRelatedObjectPopup``
    or ``window.opener.dismissChangeRelatedObjectPopup`` (Django-compatible).

- Supports **nested popups**: forwards ``postMessage`` responses up the chain.
- Exposes ``window.PopupResponse`` for external use:

.. code-block:: javascript

   window.PopupResponse.state;       // Current popup context state
   window.PopupResponse.getPopupValue();  // PK of the object being edited
   window.PopupResponse.getPopupLabel();  // Display label for the object
   window.PopupResponse.send(pk, label);  // Manually send a popup response

**Global functions registered by** ``popup_response.js``:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Function
     - Description
   * - ``dismissAddRelatedModal(pk, label)``
     - Called by child iframes to add the new object to the parent Select2 field.
   * - ``dismissPopup(pk, obj)``
     - Generic fallback, forwards response up the window chain.
   * - ``dismissAddRelatedObjectPopup(win, pk, str)``
     - Django admin compatibility shim (traditional add popup).
   * - ``dismissChangeRelatedObjectPopup(win, pk, str, newId)``
     - Django admin compatibility shim (traditional change popup).

**Customization:**

Override ``templates/admin/change_form.html`` in your project.

Change Password Page (change_password.html)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beautiful form for changing user passwords.

**Features:**

- Centered card layout
- Current password field
- New password fields with confirmation
- Password requirements display
- Error messages
- Submit button

**Customization:**

Override ``templates/admin/change_password.html`` in your project.

Delete Confirmation Page (delete_confirmation.html)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Confirmation page when deleting objects.

**Features:**

- Warning design with red accents
- Large warning icon
- Lists objects being deleted
- Handles protected object constraints
- Clear confirmation button
- Cancel button

**Customization:**

Override ``templates/admin/delete_confirmation.html`` in your project.

Base Site Template (base_site.html)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Main layout for all admin pages.

**Features:**

- Collapsible sidebar navigation
- Top navigation bar (topbar)
- Sidebar toggle button
- User dropdown menu
- App and model navigation
- Responsive design

**Layout:**

.. code-block:: 

   ┌─────────────────────────────────┐
   │         Topbar                  │
   │  [≡] Title        [User] [⋮]    │
   ├──────────┬─────────────────────┤
   │          │                     │
   │ Sidebar  │   Main Content      │
   │          │                     │
   │ - Apps   │                     │
   │ - Models │                     │
   │          │                     │
   └──────────┴─────────────────────┘

**Customization:**

Override ``templates/admin/base_site.html`` in your project.

Dashboard/Index Page (index.html)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main dashboard/homepage when accessing admin.

**Default Content:**

- Welcome message
- List of app modules
- Quick access to recently added items

**Customization:**

Override ``templates/admin/index.html`` in your project to create a custom dashboard.

Sidebar Features
================

**Navigation:**

- Organized by app
- Model listings with icon
- "Add" button for each model
- Active state highlighting
- Collapsible on mobile
- Smooth toggle animation
- Custom links section (see ``custom_links`` in :ref:`palette-admin-settings`)

**Toggle:**

Click the hamburger menu (≡) in the topbar to collapse/expand the sidebar.

**Mobile:**

On mobile devices, the sidebar collapses automatically and can be toggled.

**Desktop:**

The sidebar is always visible and can be toggled with localStorage persistence.

**Custom Links:**

Arbitrary links can be injected into the sidebar below the Dashboard entry via
``PALETTE_ADMIN_SETTINGS['custom_links']``. Each link accepts:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Key
     - Description
   * - ``label``
     - Display text for the link.
   * - ``url``
     - Named URL pattern (e.g. ``'admin:support_chat'``) **or** a raw path/URL.
       Named patterns are resolved with ``reverse()`` at request time; unresolvable
       values fall back to the raw string.
   * - ``left_icon``
     - *(optional)* Bootstrap Icon class rendered before the label (e.g. ``'bi bi-headset'``).
   * - ``right_icon``
     - *(optional)* Bootstrap Icon class rendered after the label (e.g. ``'bi bi-arrow-right'``).

The active state is applied automatically when ``resolved_url`` matches ``request.path``.

Customizing the Admin Interface
================================

**Override Individual Templates**

Create your own version in your project:

.. code-block:: 

   your_project/
   ├── templates/
   │   └── admin/
   │       ├── base_site.html          # Override base
   │       ├── index.html              # Override dashboard
   │       ├── change_list.html        # Override list view
   │       └── change_form.html        # Override form
   └── ...

**Customize Colors**

Edit the CSS in the template ``<style>`` block to change colors:

.. code-block:: django

   <style>
     :root {
       --primary: #0d6efd;
       --danger: #dc3545;
       --success: #198754;
     }
   </style>

**Customize Logo**

Set the site logo in your custom ``base_site.html``:

.. code-block:: django

   {% if site_logo %}
     <img src="{{ site_logo }}" alt="Logo">
   {% elif site_icon %}
     <i class="{{ site_icon }}"></i>
   {% endif %}

**Customize Site Header**

In your custom ``base_site.html``:

.. code-block:: django

   <h1>My Custom Admin</h1>

**Add Custom CSS**

Create your own CSS file and include it:

.. code-block:: django

   <link rel="stylesheet" href="{% static 'css/my-custom-admin.css' %}">

Static Files
============

All static files are included and bundled:

**CSS Files:**

- Bootstrap 5 (bootstrap.min.css)
- Bootstrap Icons (bootstrap-icons.css)
- Custom admin styling
- Select2 styling

**JavaScript Files:**

- Bootstrap Bundle (bootstrap.bundle.min.js)
- jQuery (jquery.slim.min.js)
- Select2 (select2.min.js)
- HTMX (htmx.min.js)

**Fonts:**

- Bootstrap Icons font files

All files are automatically available after ``collectstatic``.

.. _palette-admin-settings:

Configuration
=============

All Palette Admin settings are controlled through a single ``PALETTE_ADMIN_SETTINGS``
dictionary in your project's ``settings.py``.

.. code-block:: python

   # settings.py
   PALETTE_ADMIN_SETTINGS = {
       'site_header':  'My Project',
       'site_title':   'My Project Admin',
       'site_icon':    'bi bi-grid',
       'index_title':  'Dashboard',
       'app_icons':    { ... },
       'model_icons':  { ... },
       'hidden_apps':  [ ... ],
       'hidden_models': { ... },
       'custom_links': [ ... ],
   }

All keys are optional. Omitted keys fall back to built-in defaults.

.. list-table:: Top-level keys
   :header-rows: 1
   :widths: 25 15 60

   * - Key
     - Type
     - Description
   * - ``site_header``
     - ``str``
     - Displayed in the sidebar header and browser tab.
   * - ``site_title``
     - ``str``
     - HTML ``<title>`` for admin pages.
   * - ``site_icon``
     - ``str``
     - Bootstrap Icon class used when no ``site_logo`` is set (e.g. ``'bi bi-palette'``).
   * - ``index_title``
     - ``str``
     - Heading shown on the dashboard page.
   * - ``app_icons``
     - ``dict``
     - Maps ``app_label`` → Bootstrap Icon class. See `App & Model Icons`_.
   * - ``model_icons``
     - ``dict``
     - Maps ``model_name`` → Bootstrap Icon class. See `App & Model Icons`_.
   * - ``hidden_apps``
     - ``list``
     - App labels to exclude from the sidebar. See `Hiding Apps and Models`_.
   * - ``hidden_models``
     - ``dict``
     - Per-app lists of model names to exclude from the sidebar. See `Hiding Apps and Models`_.
   * - ``custom_links``
     - ``list``
     - Extra links rendered in the sidebar below the Dashboard entry. See `Sidebar Features`_.

App & Model Icons
-----------------

Palette Admin ships with a set of built-in icons for common app and model names.
You can override any of them or add new ones via ``PALETTE_ADMIN_SETTINGS``.

**Per-app icons** — keyed by Django's ``app_label``:

.. code-block:: python

   PALETTE_ADMIN_SETTINGS = {
       'app_icons': {
           'blog':  'bi bi-journal-richtext',
           'shop':  'bi bi-bag',
           'myapp': 'bi bi-star',
       },
   }

**Per-model icons** — keyed by Django's ``model_name`` (lowercase, singular):

.. code-block:: python

   PALETTE_ADMIN_SETTINGS = {
       'model_icons': {
           'post':    'bi bi-file-text',
           'product': 'bi bi-box',
           'user':    'bi bi-person',
       },
   }

**App-specific model icon override** — use ``app_label.model_name`` as the key to
override an icon for a model in a particular app only (takes priority over the plain
``model_name`` key):

.. code-block:: python

   PALETTE_ADMIN_SETTINGS = {
       'model_icons': {
           'user':      'bi bi-person',           # default for all User models
           'auth.user': 'bi bi-shield-person',    # overrides for auth.User specifically
       },
   }

User-supplied icons are **merged** with the built-in defaults, so you only need to
specify the ones you want to change. Built-in defaults include icons for common
app labels (``auth``, ``blog``, ``shop``, ``accounts``, etc.) and model names
(``user``, ``group``).

Hiding Apps and Models
----------------------

Remove entire apps from the sidebar:

.. code-block:: python

   PALETTE_ADMIN_SETTINGS = {
       'hidden_apps': ['sessions', 'contenttypes', 'admin'],
   }

Remove specific models from an app while keeping the rest of the app visible:

.. code-block:: python

   PALETTE_ADMIN_SETTINGS = {
       'hidden_models': {
           'auth':  ['permission'],          # hide Permission; keep User & Group
           'blog':  ['tag', 'draft'],
       },
   }

Keys in ``hidden_models`` are ``app_label`` strings; values are lists of
``model_name`` strings (lowercase, singular — same as Django's ``Model._meta.model_name``).

Filtering happens at the ``get_app_list`` level, so hidden items are excluded
everywhere the app list is used (sidebar, dashboard, breadcrumbs).

Custom Sidebar Links
--------------------

.. code-block:: python

   PALETTE_ADMIN_SETTINGS = {
       'custom_links': [
           {
               'label': 'Support',
               'url':   'admin:support_chat',      # named URL pattern
               'left_icon': 'bi bi-headset',
           },
           {
               'label': 'Documentation',
               'url':   'https://docs.example.com',  # absolute URL also works
               'left_icon':  'bi bi-book',
               'right_icon': 'bi bi-box-arrow-up-right',
           },
       ],
   }

Named URL patterns are resolved with ``reverse()`` at request time. If the name
cannot be resolved (e.g. the URL doesn't exist), the raw value is used as-is.

**Custom Admin Site**

You can subclass ``PaletteAdminSite`` for further programmatic customisation:

.. code-block:: python

   # myapp/admin.py
   from dj_palette.palette_admin.site import PaletteAdminSite

   class MyAdminSite(PaletteAdminSite):
       site_header = "My Admin"
       site_title = "My Project"

   my_admin_site = MyAdminSite(name="myadmin")

   # In urls.py
   from django.urls import path
   from myapp.admin import my_admin_site

   urlpatterns = [
       path('admin/', my_admin_site.urls),
   ]

Extending the Admin Interface
==============================

**Add Custom Pages**

Create custom admin pages by extending the admin URLconf:

.. code-block:: python

   # myapp/admin.py
   from django.contrib import admin
   from django.urls import path
   from django.views.generic import TemplateView

   class MyAdminSite(admin.AdminSite):
       def get_urls(self):
           urls = super().get_urls()
           custom_urls = [
               path('reports/', self.admin_site_view(self.reports_view), name='reports'),
           ]
           return custom_urls + urls

       def reports_view(self, request):
           return TemplateView.as_view(template_name='admin/reports.html')(request)

**Add Custom Components**

Create components for your admin interface:

.. code-block:: django

   {% load palette %}

   {% palette_component "dashboard_card" %}
     <div class="card">
       <div class="card-body">
         {% palette_block "content" %}
           {{ content }}
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

Responsive Design
=================

The admin interface is fully responsive:

**Desktop (>= 1200px)**

- Full sidebar always visible
- Multi-column layouts
- All features accessible
- Hover effects

**Tablet (768px - 1199px)**

- Sidebar visible but narrower
- Two-column layouts when possible
- Touch-friendly buttons
- All features accessible

**Mobile (< 768px)**

- Collapsible sidebar
- Single-column layouts
- Large, touch-friendly buttons
- Optimized form fields
- Readable font sizes

Performance
===========

**Optimized CSS:**

- Minimal CSS (only what's needed)
- No unused Bootstrap classes
- Optimized images
- Inline critical CSS

**Optimized JavaScript:**

- Minimal dependencies
- Lazy loading where possible
- Efficient selectors
- No jQuery for core functionality

**Static File Caching:**

- Versioned assets
- Long expiration headers (when deployed)
- Gzipped files
- CDN-friendly

Accessibility
==============

The admin interface is accessible:

- **WCAG 2.1 AA** compliance target
- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support
- Color contrast requirements met
- Form labels properly associated

Browser Support
===============

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

Troubleshooting
===============

**Static Files Not Loading**

1. Run ``python manage.py collectstatic``
2. Check STATIC_URL setting
3. Check STATICFILES_DIRS setting
4. Check DEBUG = True in development

**Sidebar Not Appearing**

1. Make sure ``dj_palette.palette_admin`` is in INSTALLED_APPS
2. Check that base_site.html is being used
3. Clear browser cache
4. Run ``collectstatic`` again

**Forms Not Styled**

1. Run ``collectstatic``
2. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
3. Check browser console for errors
4. Check that Bootstrap CSS is loading

Getting Help
============

- Read the full documentation at https://django-palette.readthedocs.io
- Check the GitHub repository: https://github.com/ogofe/django-palette
- Open an issue on GitHub: https://github.com/ogofe/django-palette/issues
