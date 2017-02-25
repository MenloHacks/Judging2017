from django.shortcuts import render, redirect
from django.views.generic import View
import models
import forms
import numpy as np

def complete(request):
    return render(request, "complete.html")


def rankings(request):
    project_info = []
    for project in models.Project.objects.all():
        ratings = models.Rating.objects.filter(project_id=project.id)
        count = 0
        rating_sum = np.array([0., 0., 0., 0.])
        for rating in ratings:
            if rating.passed:
                continue
            rating_sum += [float(rating.standardized_originality),
                           float(rating.standardized_usefulness),
                           float(rating.standardized_technical_difficulty),
                           float(rating.standardized_polish)]
            count += 1
        rating_sum /= count
        project_info.append([project.name] + list(rating_sum) +
                            [np.mean(rating_sum)])
    return render(request, "ranking.html", context={"ratings": project_info})




class Overview(View):

    def get(self, request):
        session_key = request.session.session_key
        if not session_key:  # User doesn't have a session
            request.session.save()  # Create new session
            session_key = request.session.session_key
        ratings = []
        for project in models.Project.objects.all():
            try:
                rating = models.Rating.objects.get(judge_id=session_key,
                                                   project_id=project.id)
                # get the rating for this project from this judge. There should
                # always be one unique rating
                if rating.passed:  # the judge has decided to skip this project
                    passed = "Passed"
                    ratings.append([project.id,
                                    [project.name, passed, passed, passed,
                                     passed]])
                else:
                    ratings.append([project.id, [project.name, rating.originality,
                                                 rating.usefulness,
                                                 rating.technical_difficulty,
                                                 rating.polish]])
            except models.Rating.DoesNotExist:  # There is no rating currently
                # for this judge and this user
                not_rated = "Not yet rated"
                ratings.append([project.id,
                                [project.name, not_rated, not_rated, not_rated,
                                 not_rated]])

        return render(request, "overview.html", context={"ratings": ratings})

    def post(self, request):  # SUBMIT TO THE STANDARDIZATION!
        if request.POST.get("submitted"):  # should always be true with this
                # version
            judge_id = request.session.session_key
            ratings = models.Rating.objects.filter(
                judge_id=judge_id).exclude(passed=True)

            rating_array = []
            for rating in ratings:
                rating_array.append([rating.originality, rating.usefulness,
                                     rating.technical_difficulty,
                                     rating.polish])

            rating_array = np.array(rating_array)
            coefficients = [[],[]]
            for column in rating_array.T: #find the mean and std multiplier
                # for each column
                coefficients[0].append(np.mean(column))
                coefficients[1].append(3/np.std(column))

            for rating in ratings: #find the standardized ratings
                rating.standardized_originality = \
                    (rating.originality-coefficients[0][0]) * \
                    coefficients[1][0] + 5

                rating.standardized_usefulness = \
                    (rating.usefulness - coefficients[0][1]) * \
                    coefficients[1][1] + 5

                rating.standardized_technical_difficulty = \
                    (rating.technical_difficulty - coefficients[0][2]) * \
                    coefficients[1][2] + 5

                rating.standardized_polish = \
                    (rating.polish - coefficients[0][3]) * \
                    coefficients[1][3] + 5
                rating.save()
        return complete(request)




class RatingView(View):

    def get(self, request, project_id):
        try:
            project_name = models.Project.objects.get(id=project_id).name
        except models.Project.DoesNotExist:
            return redirect("/")
        session_key = request.session.session_key
        passed = False
        try:
            # get the judge's current rating
            rating_model = models.Rating.objects.get(project_id=project_id,
                                                     judge_id=session_key)
            if rating_model.passed:
                passed = True
        except models.Rating.DoesNotExist:  # judge hasn't rated project
            # yet; use empty model.
            rating_model = None
        rating_form = forms.RatingForm(instance=rating_model)

        return render(request, "rating.html",
                      context={"rating_form": rating_form,
                               "project_name": project_name,
                               "project_id": project_id,
                               "passed": passed})

    def post(self, request, project_id):
        session_key = request.session.session_key

        if request.POST.get("passed"): # Save a mostly empty db entry with
            # passed set to True
            rating_model = models.Rating()
            rating_model.passed = True
        else:
            rating_form = forms.RatingForm(request.POST)
            if rating_form.is_valid():
                rating_model = rating_form.save(commit=False)
            else:  # this should never happen bc javascript validation
                return self.get(request, project_id)

        try:
            models.Rating.objects.get(project_id=project_id,
                                      judge_id=session_key).delete()
            # if there's an existing record, kill it.
        except models.Rating.DoesNotExist:
            pass

        rating_model.project_id = project_id
        rating_model.judge_id = session_key
        rating_model.save()
        return self.get(request, project_id)
