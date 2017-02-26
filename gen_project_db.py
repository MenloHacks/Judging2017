# Setup Django settings and models
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Judging.settings")

import django
django.setup()

# Begin program
from JudgingSystem import models
from django.contrib.sessions.models import Session

import json

f = open("projects.json", "r")
data = json.loads(f.read())

for project in models.Project.objects.all():
    project.delete()

for session in Session.objects.all():
    session.delete()

for i, data in enumerate(data):
    project = models.Project()
    project.id = i
    project.name = data
    project.save()