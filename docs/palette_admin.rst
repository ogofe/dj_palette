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

**File Upload:**

The file input includes:

- Drag-and-drop zone
- Click to browse
- Image preview for image files
- File icon for other file types
- Responsive grid preview
- Works with any file type

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

**Toggle:**

Click the hamburger menu (≡) in the topbar to collapse/expand the sidebar.

**Mobile:**

On mobile devices, the sidebar collapses automatically and can be toggled.

**Desktop:**

The sidebar is always visible and can be toggled with localStorage persistence.

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

Configuration
=============

**Site Header**

Customize the admin site header:

.. code-block:: python

   # In your admin configuration
   admin.site.site_header = "My Custom Admin"

**Site Title**

Customize the browser tab title:

.. code-block:: python

   admin.site.site_title = "My Project Admin"

**Index Title**

Customize the dashboard title:

.. code-block:: python

   admin.site.index_title = "Dashboard"

**Enable/Disable Apps**

Control which apps are shown in the sidebar by registering model admins:

.. code-block:: python

   # In your admin.py
   admin.site.register(MyModel, MyModelAdmin)

**Custom Admin Site**

You can create a custom admin site:

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
