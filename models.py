from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    layout_json = models.TextField(help_text="JSON describing component layout")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Component(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    default_props = models.JSONField(default=dict)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.display_name
