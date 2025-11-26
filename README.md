# 🎨 django-palette

<p align="center">
  <img src="logo.jpg" alt="Django Palette Logo" width="200">
</p>

A powerful Django admin interface framework with beautiful Bootstrap styling, reusable components, and custom template tags for building elegant admin pages.

**django-palette** is a Django package that enhances the admin interface with modern Bootstrap 5 templates, responsive layouts, and a flexible component-based templating system. It provides custom admin templates, sidebar navigation, and reusable UI components while maintaining full Django admin functionality.

---

## ✨ Features

- 🎨 **Beautiful Bootstrap Admin Interface** - Modern, responsive admin templates with Bootstrap 5 styling
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- 🧩 **Reusable Components** - Build custom UI components with the `palette_component` tag
- 🔄 **Component Slots** - Define and override content blocks within components using `palette_block` and `palette_override`
- 🎯 **Template Tags** - Custom tags for rendering and managing components with context variables
- 📊 **Enhanced Admin Pages** - Pre-styled templates for change_list, change_form, login, password change, and delete confirmation
- 🔐 **Django Admin Integration** - Full compatibility with Django's permissions and admin system
- 📁 **Sidebar Navigation** - Collapsible sidebar with app and model navigation
- 🎨 **Drag-and-drop File Upload** - Modern file upload interface with image preview
- 🔍 **Grid/List Toggle Views** - Multiple view modes for displaying model lists
- ⚡ **Zero Breaking Changes** - Works alongside existing Django admin setup

---

## 📦 Installation

```bash
pip install dj-palette
```

---

## ⚙️ Quick Setup

### 1. Add to `INSTALLED_APPS`

In your `settings.py`:

```python
INSTALLED_APPS = [
    'dj_palette',  # Core palette app
    'dj_palette.palette_admin',  # Beautiful admin interface
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # ... other apps
]
```

### 2. Configure Admin URL

In your `urls.py`:

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # or use the custom palette admin site:
    # from dj_palette.palette_admin.site import palette_admin_site
    # path('admin/', palette_admin_site.urls),
]
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Collect Static Files

```bash
python manage.py collectstatic
```

---

## 🧩 Custom Template Tags

### `palette_component` - Define a Reusable Component

Define a component with named blocks that can be overridden:

```django
{% load palette %}

{% palette_component "admin_card" %}
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      {% palette_block "card_content" %}
        <h5 class="card-title">{{ title }}</h5>
        <p class="card-text">{{ content }}</p>
      {% endpalette_block %}
    </div>
  </div>
{% endpalette_component %}
```

### `palette_ui` - Render a Component with Props

Render the component and pass context variables:

```django
{% load palette %}

{% palette_ui "admin_card" with title="Total Users" content="1,234" %}
```

### `palette_override` - Override Component Blocks

Override specific blocks when rendering a component:

```django
{% load palette %}

{% palette_ui "admin_card" with title="Active Users" %}
  {% palette_override "card_content" %}
    <h5 class="card-title">Active Users</h5>
    <p class="card-text">{{ active_count }}</p>
    <small class="text-muted">Last updated: {{ last_updated }}</small>
  {% endpalette_override %}
{% endpalette_ui %}
```

### `palette_block` - Define Overridable Content Areas

Create named blocks within components for customization:

```django
{% palette_block "footer" %}
  <div class="card-footer text-muted">
    {{ footer_text|default:"No additional info" }}
  </div>
{% endpalette_block %}
```

---

## 🎨 Admin Templates Included

The package includes beautiful Bootstrap-styled templates for:

- **change_list.html** - Model list view with grid/list toggle
- **change_form.html** - Add/edit form with file upload dropzone
- **change_password.html** - Password change form
- **delete_confirmation.html** - Delete confirmation dialog
- **login.html** - Login page with modern gradient design
- **base_site.html** - Custom admin base with collapsible sidebar
- **index.html** - Dashboard/home page

All templates maintain full Django admin functionality while providing a modern, responsive interface.

---

## 📊 Built-in Filters

### `admin_fields` Filter

Display object fields as a list of tuples:

```django
{% load palette %}

{% for field_name, field_value in object|admin_fields %}
  <p><strong>{{ field_name }}:</strong> {{ field_value }}</p>
{% endfor %}
```

### `admin_field` Filter

Get a specific field value from an object:

```django
{{ object|admin_field:"email" }}
```

---

## 💡 Usage Examples

### Example 1: Custom Component Definition

Create a file `templates/components/stat_card.html`:

```django
{% load palette %}

{% palette_component "stat_card" %}
  <div class="card stat-card border-0 shadow-sm">
    <div class="card-body text-center">
      {% palette_block "stat_number" %}
        <h2 class="display-4 text-primary">{{ number }}</h2>
      {% endpalette_block %}
      
      {% palette_block "stat_label" %}
        <p class="text-muted">{{ label }}</p>
      {% endpalette_block %}
    </div>
  </div>
{% endpalette_component %}
```

### Example 2: Using the Component

In your template:

```django
{% load palette %}

<div class="row">
  <div class="col-md-4">
    {% palette_ui "stat_card" with number="1,234" label="Total Users" %}
  </div>
  
  <div class="col-md-4">
    {% palette_ui "stat_card" with number="89" label="Active Today" %}
      {% palette_override "stat_number" %}
        <h2 class="display-4 text-success">{{ number }}</h2>
      {% endpalette_override %}
    {% endpalette_ui %}
  </div>
</div>
```

### Example 3: Context Variables from Django

Pass context variables directly:

```django
{% load palette %}

{% palette_ui "stat_card" with number=total_users label="Total Users" %}

{% palette_ui "stat_card" with number=active_sessions label="Active Sessions" %}
```

---

## 🎯 Features in Detail

### Responsive Admin Interface
- Mobile-friendly design with collapsible sidebar
- Touch-friendly buttons and controls
- Optimized for all screen sizes

### Component System
- Define reusable UI components once
- Render them multiple times with different data
- Override specific sections without redefining entire components
- Clean separation of concerns

### Modern Bootstrap Styling
- Bootstrap 5 framework
- Bootstrap Icons integration
- Consistent color scheme
- Professional gradients and shadows

### Enhanced Form Handling
- Drag-and-drop file upload with preview
- Better date/time pickers
- Responsive form layouts
- Inline error messages

### Grid/List View Toggle
- Switch between grid and list views
- Persistent view preference (localStorage)
- Optimized for different data types
- Beautiful card-based layout

---

## 🔧 Configuration

Customize the admin interface by extending templates or creating your own components. All templates are overridable in your project's template directory.

Create `templates/admin/base_site.html` in your project to customize the site header, logo, or color scheme.

---

## 🖼️ Static Files

The package includes:
- Bootstrap 5 CSS and JS
- Bootstrap Icons
- Custom admin styling
- HTMX for dynamic interactions
- Select2 for better selects

All static files are included and automatically available after `collectstatic`.

---

## 🤝 Contributing

Want to contribute? We'd love your help!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit (`git commit -am 'Add amazing feature'`)
5. Push (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📄 License

MIT License © 2025 Joel O. Tanko

See LICENSE file for details.

---

## 📚 Documentation & Links

- **GitHub**: [https://github.com/ogofe/django-palette](https://github.com/ogofe/django-palette)
- **PyPI**: [https://pypi.org/project/dj-palette/](https://pypi.org/project/dj-palette/)
- **Documentation**: [https://django-palette.readthedocs.io](https://django-palette.readthedocs.io)
- **Issues**: [https://github.com/ogofe/django-palette/issues](https://github.com/ogofe/django-palette/issues)

---

## 🚀 Getting Help

- **Found a bug?** Open an issue on [GitHub](https://github.com/ogofe/django-palette/issues)
- **Have a question?** Check the [documentation](https://django-palette.readthedocs.io)
- **Want to chat?** Reach out via email: 7thogofe@gmail.com

---

Made with ❤️ for the Django community
