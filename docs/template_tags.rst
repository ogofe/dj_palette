==============
Template Tags
==============

Django Palette provides custom template tags for building dynamic, reusable admin components.

Loading the Template Tag Library
=================================

Add this to the top of any template using django-palette tags:

.. code-block:: django

   {% load palette %}

palette_component
=================

Define a reusable component with named blocks.

**Syntax:**

.. code-block:: django

   {% palette_component component_name %}
     <!-- Component HTML -->
     {% palette_block block_name %}
       Default content
     {% endpalette_block %}
   {% endpalette_component %}

**Parameters:**

- ``component_name`` (required): Name of the component (unquoted identifier)

**Description:**

Creates a new component that can be rendered multiple times with ``palette_ui``. Components can have multiple ``palette_block`` areas that can be overridden when the component is rendered.

**Example:**

.. code-block:: django

   {% palette_component stat_card %}
     <div class="card border-0 shadow-sm">
       <div class="card-body text-center">
         {% palette_block header %}
           <h2 class="display-4">{{ number }}</h2>
         {% endpalette_block %}
         
         {% palette_block footer %}
           <p class="text-muted">{{ label }}</p>
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

**Best Practices:**

- Define components in a template file that's included from your base template
- Use clear, descriptive component names
- Use clear block names (e.g., ``header``, ``content``, ``footer``)
- Provide sensible default content in blocks

palette_block
=============

Define a named block within a component that can be overridden.

**Syntax:**

.. code-block:: django

   {% palette_block block_name %}
     Default content here
   {% endpalette_block %}

**Parameters:**

- ``block_name`` (required): Name of the block (unquoted identifier)

**Description:**

Creates a named area within a component that can be overridden when rendering. Each block must have a unique name within its component.

**Example:**

.. code-block:: django

   {% palette_block content %}
     <p>This is the default content.</p>
   {% endpalette_block %}

When rendering the component, you can override this block:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="card" %}
     {% palette_override content %}
       <p>This is custom content that replaces the default.</p>
     {% endpalette_override %}
   {% endpalette_ui %}

**Block Naming:**

Use descriptive names:

- ``header`` - Header section
- ``content`` - Main content area
- ``footer`` - Footer section
- ``actions`` - Action buttons
- ``metadata`` - Additional information

palette_ui
==========

Render a component with context variables and optional overrides.

**Syntax:**

.. code-block:: django

   {% palette_ui file="path/to/template.html" component="component_name" with var1=value1 var2=value2 %}

**Parameters:**

- ``file`` (required): Path to the template file containing the component definition
- ``component`` (required): Name of the component to render (unquoted identifier)
- ``with`` (optional): Pass context variables to the component
- Variables follow Django's ``with`` tag syntax

**Description:**

Renders a previously defined component. You can pass context variables that will be available inside the component. You can also override specific blocks using ``palette_override``.

**Example 1: Basic Rendering**

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="stat_card" with number="1,234" label="Total Users" %}

This renders the ``stat_card`` component with:
- ``number`` = "1,234"
- ``label`` = "Total Users"

Inside the component, you can access these variables:

.. code-block:: django

   <h2>{{ number }}</h2>
   <p>{{ label }}</p>

**Example 2: With Overrides**

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="stat_card" with number="89" label="Active Today" %}
     {% palette_override header %}
       <h2 class="text-success">{{ number }}</h2>
     {% endpalette_override %}
   {% endpalette_ui %}

**Example 3: With Django Variables**

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="stat_card" with number=total_users label="Total Users" %}
   {% palette_ui file="palette/components/card.html" component="stat_card" with number=active_count label="Active Sessions" %}

**Variable Types:**

You can pass any type of value:

- Strings: ``label="My Label"``
- Numbers: ``count=123``
- Variables: ``count=total_users``
- Objects: ``user=request.user``
- Filters: ``date=now|date:"Y-m-d"``

palette_override
================

Override a specific block when rendering a component.

**Syntax:**

.. code-block:: django

   {% palette_ui file="path/to/template.html" component="component_name" %}
     {% palette_override block_name %}
       New content for the block
     {% endpalette_override %}
   {% endpalette_ui %}

**Parameters:**

- ``block_name`` (required): Name of the block to override (unquoted identifier)

**Description:**

Replaces the content of a named block within a component. Can only be used inside ``palette_ui``. You can have multiple overrides for different blocks.

**Example 1: Single Override**

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="card" %}
     {% palette_override content %}
       <p>Custom content goes here</p>
     {% endpalette_override %}
   {% endpalette_ui %}

**Example 2: Multiple Overrides**

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="card" with title="My Card" %}
     {% palette_override header %}
       <h1 class="text-primary">{{ title }}</h1>
     {% endpalette_override %}
     
     {% palette_override content %}
       <p>Custom content in the body</p>
     {% endpalette_override %}
     
     {% palette_override footer %}
       <small>Custom footer text</small>
     {% endpalette_override %}
   {% endpalette_ui %}

**Override with Variables:**

You have access to all variables passed to ``palette_ui``:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="stat_card" with number=count label="My Stat" %}
     {% palette_override header %}
       <h2 class="text-info">{{ number }}</h2>
     {% endpalette_override %}
   {% endpalette_ui %}

Complete Example
================

Here's a complete example showing all tags working together:

**Component Definition** (in ``templates/components/alert.html``)

.. code-block:: django

   {% load palette %}

   {% palette_component alert %}
     <div class="alert alert-{{ type|default:'info' }} border-0" role="alert">
       {% palette_block icon %}
         <i class="bi bi-info-circle"></i>
       {% endpalette_block %}
       
       {% palette_block title %}
         <strong>{{ title }}</strong>
       {% endpalette_block %}
       
       {% palette_block message %}
         {{ message }}
       {% endpalette_block %}
     </div>
   {% endpalette_component %}

**Using the Component**

.. code-block:: django

   {% load palette %}
   {% include "components/alert.html" %}

   <!-- Basic usage -->
   {% palette_ui file="palette/components/alert.html" component="alert" with type="success" title="Success!" message="Your changes have been saved." %}

   <!-- With overrides -->
   {% palette_ui file="palette/components/alert.html" component="alert" with type="warning" title="Attention" message="Please review before proceeding." %}
     {% palette_override icon %}
       <i class="bi bi-exclamation-triangle"></i>
     {% endpalette_override %}
   {% endpalette_ui %}

   <!-- With variables -->
   {% palette_ui file="palette/components/alert.html" component="alert" with type=alert_type title=alert_title message=alert_message %}

Tips & Tricks
=============

**1. Reuse Components Everywhere**

Define common components once, use them throughout your templates:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="card" with title="Users" content=user_count %}
   {% palette_ui file="palette/components/card.html" component="card" with title="Orders" content=order_count %}
   {% palette_ui file="palette/components/card.html" component="card" with title="Sales" content=total_sales %}

**2. Use Variables from Context**

Pass context variables directly without quotes:

.. code-block:: django

   {% palette_ui "stat_card" with number=request.user.post_count label="Posts" %}

**3. Apply Filters to Variables**

You can apply Django filters:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="stat_card" with created=object.created_at|date:"Y-m-d" %}

**4. Create Component Variants**

Use overrides to create variations without duplicating code:

.. code-block:: django

   <!-- Success variant -->
   {% palette_ui file="palette/components/alert.html" component="alert" with type="success" title="Success" %}

   <!-- Error variant -->
   {% palette_ui file="palette/components/alert.html" component="alert" with type="danger" title="Error" %}
     {% palette_override icon %}
       <i class="bi bi-x-circle"></i>
     {% endpalette_override %}
   {% endpalette_ui %}

**5. Nest Components**

You can use components inside other components:

.. code-block:: django

   {% palette_component dashboard %}
     <div class="dashboard">
       {% palette_block stats %}
         {% palette_ui file="palette/components/card.html" component="stat_card" with number="100" label="Stat 1" %}
         {% palette_ui file="palette/components/card.html" component="stat_card" with number="200" label="Stat 2" %}
       {% endpalette_block %}
     </div>
   {% endpalette_component %}

**6. Conditional Content in Blocks**

Use Django's template conditionals inside blocks:

.. code-block:: django

   {% palette_block actions %}
     {% if user.is_staff %}
       <button>Admin Action</button>
     {% endif %}
   {% endpalette_block %}

Common Patterns
===============

**Pattern 1: Card Component**

.. code-block:: django

   {% palette_component card %}
     <div class="card border-0 shadow-sm">
       <div class="card-header">
         {% palette_block title %}
           <h5>{{ title }}</h5>
         {% endpalette_block %}
       </div>
       <div class="card-body">
         {% palette_block content %}
           <p>{{ content }}</p>
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

**Pattern 2: List Item Component**

.. code-block:: django

   {% palette_component list_item %}
     <li class="list-group-item">
       {% palette_block primary %}
         <strong>{{ name }}</strong>
       {% endpalette_block %}
       
       {% palette_block secondary %}
         <small class="text-muted">{{ description }}</small>
       {% endpalette_block %}
     </li>
   {% endpalette_component %}

**Pattern 3: Modal Component**

.. code-block:: django

   {% palette_component modal %}
     <div class="modal fade" id="{{ modal_id }}" tabindex="-1">
       <div class="modal-dialog">
         <div class="modal-content">
           <div class="modal-header">
             {% palette_block title %}
               <h5 class="modal-title">{{ title }}</h5>
             {% endpalette_block %}
           </div>
           <div class="modal-body">
             {% palette_block body %}
               {{ content }}
             {% endpalette_block %}
           </div>
           <div class="modal-footer">
             {% palette_block actions %}
               <button type="button" class="btn btn-secondary">Close</button>
             {% endpalette_block %}
           </div>
         </div>
       </div>
     </div>
   {% endpalette_component %}
