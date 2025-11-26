from django.db import models

# Create your models here.
class AdminPage(models.Model):
	name=models.CharField(max_length=200, blank=True, null=True)
	route=models.CharField(max_length=200, blank=True, null=True)
	components=models.ManyToManyField("Component", blank=True)
	content=models.TextField(blank=True, null=True)

class Component(models.Model):
	name=models.CharField(max_length=200, blank=True, null=True)
	components=models.ManyToManyField("self", blank=True)

