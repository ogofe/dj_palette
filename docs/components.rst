==========
Components
==========

Components are the core building block of django-palette. Learn how to create and use them effectively.

What is a Component?
====================

A component is a reusable piece of UI defined once and rendered multiple times with different data. It's similar to a function in programming - you define it once, then call it with different arguments.

**Basic Structure:**

.. code-block:: django

   {% palette_component component_name %}
     <!-- HTML structure with blocks -->
     {% palette_block block_name %}
       Default content
     {% endpalette_block %}
   {% endpalette_component %}

**Then render it:**

.. code-block:: django

   {% palette_ui file="path/to/template.html" component="component_name" with var1=value1 %}

Why Use Components?
===================

**Don't Repeat Yourself (DRY)**

Define a card once, use it 10 times:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="card" with title="Users" value="1,234" %}
   {% palette_ui file="palette/components/card.html" component="card" with title="Orders" value="567" %}
   {% palette_ui file="palette/components/card.html" component="card" with title="Revenue" value="$89,000" %}

**Consistency**

All instances look and behave the same way.

**Maintainability**

Change the component once, all instances are updated.

**Flexibility**

Override specific parts when needed without duplicating code.

Creating Your First Component
=============================

Let's create a simple card component.

**Step 1: Create the Template File**

Create ``templates/components/card.html``:

.. code-block:: django

   {% load palette %}

   {% palette_component card %}
     <div class="card border-0 shadow-sm">
       <div class="card-body">
         {% palette_block content %}
           <h5 class="card-title">{{ title }}</h5>
           <p class="card-text">{{ description }}</p>
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

**Step 2: Include in Your Base Template**

Include it in your base template (e.g., ``templates/admin/base_site.html``):

.. code-block:: django

   {% include "components/card.html" %}

**Step 3: Use the Component**

In any template:

.. code-block:: django

   {% load palette %}
   {% include "components/card.html" %}

   {% palette_ui file="palette/components/card.html" component="card" with title="My Card" description="This is a card" %}

That's it! Your component is now reusable.

Component Design Patterns
=========================

Pattern 1: Simple Display Card
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A card that displays information:

.. code-block:: django

   {% palette_component info_card %}
     <div class="card">
       <div class="card-body">
         {% palette_block header %}
           <h5>{{ title }}</h5>
         {% endpalette_block %}
         
         {% palette_block body %}
           <p>{{ content }}</p>
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

Usage:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="info_card" with title="Welcome" content="Hello, user!" %}

Pattern 2: Statistics Card
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display metrics or statistics:

.. code-block:: django

   {% palette_component stat_card %}
     <div class="card text-center border-0">
       <div class="card-body">
         {% palette_block metric %}
           <h2 class="display-4 text-primary">{{ value }}</h2>
         {% endpalette_block %}
         
         {% palette_block label %}
           <p class="text-muted">{{ label }}</p>
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

Usage:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="stat_card" with value="1,234" label="Total Users" %}

Pattern 3: Action Card
~~~~~~~~~~~~~~~~~~~~~~

A card with buttons or actions:

.. code-block:: django

   {% palette_component action_card %}
     <div class="card">
       <div class="card-body">
         {% palette_block title %}
           <h5>{{ title }}</h5>
         {% endpalette_block %}
         
         {% palette_block content %}
           <p>{{ content }}</p>
         {% endpalette_block %}
         
         {% palette_block actions %}
           <a href="{{ url }}" class="btn btn-primary">{{ button_text }}</a>
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

Usage:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="action_card" with title="Create New User" content="Add a new user to the system" button_text="Create User" url="/admin/auth/user/add/" %}

Pattern 4: List Item Component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Items within a list:

.. code-block:: django

   {% palette_component list_item %}
     <div class="list-group-item">
       <div class="d-flex justify-content-between">
         {% palette_block main %}
           <div>
             <h6>{{ title }}</h6>
             <small class="text-muted">{{ subtitle }}</small>
           </div>
         {% endpalette_block %}
         
         {% palette_block meta %}
           <span class="badge">{{ status }}</span>
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

Usage:

.. code-block:: django

   {% palette_ui file="palette/components/card.html" component="list_item" with title="User Name" subtitle="Email" status="Active" %}

Best Practices
==============

**1. Name Components Semantically**

Good names:
- ``card`` - Generic card
- ``stat_card`` - Statistics display
- ``user_profile`` - User profile
- ``action_button`` - Action button

Bad names:
- ``component1`` - Not descriptive
- ``tmp`` - Temporary names
- ``foo`` - Meaningless

**2. Use Clear Block Names**

Good block names:
- ``header`` - Header section
- ``content`` - Main content
- ``footer`` - Footer section
- ``actions`` - Action buttons
- ``metadata`` - Additional info

**3. Provide Sensible Defaults**

Every block should have useful default content:

.. code-block:: django

   {% palette_block "content" %}
     <p>Default content</p>
   {% endpalette_block %}

**4. Use Variables Effectively**

Pass all data as variables, don't hardcode:

.. code-block:: django

   <!-- Good -->
   {% palette_ui file="palette/components/card.html" component="card" with title=my_title content=my_content %}

   <!-- Bad -->
   {% palette_ui file="palette/components/card.html" component="card" with title="Hard coded" %}

**5. Keep Components Focused**

Each component should do one thing well:

.. code-block:: django

   <!-- Good: Card component doing card things -->
   {% palette_component card %}
     <div class="card">
       <!-- card HTML -->
     </div>
   {% endpalette_component %}

   <!-- Bad: Card component doing too much -->
   {% palette_component card %}
     <div class="card">
       <!-- card HTML -->
       <table><!-- table inside card --></table>
       <form><!-- form inside card --></form>
     </div>
   {% endpalette_component %}

**6. Make Components Reusable**

Design components for multiple use cases:

.. code-block:: django

   {% palette_component alert %}
     <div class="alert alert-{{ type }}">
       {% palette_block icon %}
         <i class="bi bi-{{ icon }}"></i>
       {% endpalette_block %}
       
       {% palette_block message %}
         <strong>{{ title }}</strong>
         <p>{{ message }}</p>
       {% endpalette_block %}
     </div>
   {% endpalette_component %}

Then use it for any alert:

.. code-block:: django

   {% palette_ui file="palette/components/alert.html" component="alert" with type="info" icon="info-circle" title="Info" message="This is information" %}
   {% palette_ui file="palette/components/alert.html" component="alert" with type="success" icon="check-circle" title="Success" message="Operation successful" %}
   {% palette_ui file="palette/components/alert.html" component="alert" with type="danger" icon="x-circle" title="Error" message="Something went wrong" %}

Organization
============

**Directory Structure:**

.. code-block:: 

   templates/
   ├── admin/
   │   ├── base_site.html
   │   └── ... other admin templates
   ├── components/
   │   ├── card.html
   │   ├── stat_card.html
   │   ├── alert.html
   │   ├── list_item.html
   │   └── ... other components
   └── ... other templates

**Include All Components**

In your base template:

.. code-block:: django

   {% include "components/card.html" %}
   {% include "components/stat_card.html" %}
   {% include "components/alert.html" %}
   {% include "components/list_item.html" %}

Advanced Techniques
====================

**Nesting Components**

Use components inside other components:

.. code-block:: django

   {% palette_component dashboard %}
     <div class="dashboard">
       {% palette_block stats %}
         {% palette_ui file="palette/components/card.html" component="stat_card" with value="100" label="Stat 1" %}
         {% palette_ui file="palette/components/card.html" component="stat_card" with value="200" label="Stat 2" %}
         {% palette_ui file="palette/components/card.html" component="stat_card" with value="300" label="Stat 3" %}
       {% endpalette_block %}
     </div>
   {% endpalette_component %}

**Conditional Content**

Use Django conditionals inside components:

.. code-block:: django

   {% palette_component user_card %}
     <div class="card">
       <div class="card-body">
         {% palette_block name %}
           {{ user.get_full_name }}
         {% endpalette_block %}
         
         {% palette_block actions %}
           {% if user.is_staff %}
             <a href="..." class="btn btn-danger">Demote</a>
           {% else %}
             <a href="..." class="btn btn-info">Promote</a>
           {% endif %}
         {% endpalette_block %}
       </div>
     </div>
   {% endpalette_component %}

**Loops in Components**

Iterate within components:

.. code-block:: django

   {% palette_component member_list %}
     <ul class="list-group">
       {% palette_block items %}
         {% for member in members %}
           {% palette_ui file="palette/components/card.html" component="list_item" with title=member.name subtitle=member.email %}
         {% endfor %}
       {% endpalette_block %}
     </ul>
   {% endpalette_component %}

**Complex Blocks**

Blocks can contain complex HTML:

.. code-block:: django

   {% palette_block footer %}
     <div class="card-footer">
       <div class="row">
         <div class="col">
           <span>{{ created_at|date:"Y-m-d" }}</span>
         </div>
         <div class="col text-end">
           <a href="{{ edit_url }}" class="btn btn-sm btn-outline-primary">Edit</a>
         </div>
       </div>
     </div>
   {% endpalette_block %}

Real-World Examples
===================

See :doc:`examples` for complete, production-ready component examples.
