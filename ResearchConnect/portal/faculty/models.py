from django.db import models

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    college = models.CharField(max_length=100, null=True, blank=True)
    profile_url = models.URLField(null=True, blank=True)
    research_areas = models.JSONField(default=list, null=True, blank=True)

    def __str__(self):
        return self.name
