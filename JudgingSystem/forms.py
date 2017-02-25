from django.forms import ModelForm
import models


class RatingForm(ModelForm):
    required_css_class = 'label-required'

    class Meta:
        model = models.Rating
        fields = ["originality", "usefulness", "technical_difficulty", "polish"]