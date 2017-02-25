from django.db import models
from django.contrib.sessions.models import Session


class Project(models.Model): # you should prepopulate this table into the DB
    name = models.CharField(max_length=150)

class Rating(models.Model):
    judge = models.ForeignKey(Session)
    project = models.ForeignKey(Project)

    originality = models.IntegerField(null=True)
    usefulness = models.IntegerField(null=True)
    technical_difficulty = models.IntegerField(null=True)
    polish = models.IntegerField(null=True)

    standardized_originality = models.DecimalField(null=True,
                                                   decimal_places=4,
                                                   max_digits=6
                                                   )
    standardized_usefulness = models.DecimalField(null=True,
                                                   decimal_places=4,
                                                   max_digits=6
                                                   )
    standardized_technical_difficulty = models.DecimalField(null=True,
                                                   decimal_places=4,
                                                   max_digits=6
                                                   )
    standardized_polish = models.DecimalField(null=True,
                                                   decimal_places=4,
                                                   max_digits=6
                                                   )

    # the judge has decided to skip this project for COI reasons probably
    passed = models.BooleanField(default=False)


