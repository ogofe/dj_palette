=========
Examples
=========

In this example, we'll create a **Youtube Snippet** object and a component that we'll use to render a Youtube Video

1. Create a snippets app:
In your terminal use the django command for creating apps to scaffold a new django app by running

.. code-block:: bash
    py manage.py startapp snippets


2. Create a Youtube Snippet model to store the Youtube videos

.. code-block:: python
    # snippets/models.py
    from django.db import models

    class YoutubeSnippet(models.Model):
        video_id = models.CharField(max_length=20)
        title = models.CharField(max_length=200)
        channel_name = models.CharField(max_length=100)
        thumbnail_url = models.URLField()

        @property
        def watch_url(self):
            return f"https://youtube.com/?watch={self.video_id}"
        
        def __str__(self):return self.title



3. Add your model to the admin:
Assuming you added ``dj_palette.palette_admin`` to ``INSTALLED_APPS``, \
 and have configured your project to use the Palette Admin dashboard, \
 you'll need to use ``palette_admin`` site to register your models.

.. code-block:: python
    # snippets/admin.py

    from dj_palette.palette_admin.admin import palette_admin, PaletteModelAdmin
    from .models import YoutubeSnippet

    class YoutubeSnippetModelAdmin(PaletteModelAdmin):
        list_display = ('title', 'url')
        list_display_links = ('title', )

    # now register your models 
    palette_admin.register(YoutubeSnippet, YoutubeSnippetModelAdmin)


4. Make migrations

.. code-block:: bash
    py manage.py makemigrations && \
    py manage.py migrate


5. Now create template file for your component in your ``snippets`` app i.e ``snippets/templates/snippets/components/cards.html`` 

.. code-block:: django
    {% load palette %}

    {% palette_component "snippet_card" %}
        
        <!-- You can override this when rendering this component -->
        {% palette_block actions %}{% endpalette_block %}
    {% endpalette_component %}

