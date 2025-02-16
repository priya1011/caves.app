from datetime import timedelta

from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Fieldset, Layout, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from logger.templatetags.logger_tags import distformat
from users.models import Notification

from .models import Trip, TripReport

User = get_user_model()


class DistanceUnitFormMixin:
    def __init__(self, *args, **kwargs):
        """
        Format all distance units using distformat

        There is a bug(?) in django-distance-field that causes distances
        to occasionally be rendered as scientific notation. Formatting using
        distformat fixes this.
        """

        instance = kwargs.get("instance", None)
        if not instance:
            return super().__init__(*args, **kwargs)

        distance_fields = [
            "horizontal_dist",
            "vert_dist_down",
            "vert_dist_up",
            "surveyed_dist",
            "resurveyed_dist",
            "aid_dist",
        ]

        units = instance.user.units
        initial = {}
        for field in distance_fields:
            initial[field] = distformat(getattr(instance, field), units)

        kwargs.update({"initial": initial})
        super().__init__(*args, **kwargs)


class TripReportForm(forms.ModelForm):
    class Meta:
        model = TripReport
        fields = [
            "title",
            "pub_date",
            "slug",
            "content",
            "privacy",
        ]
        widgets = {
            "pub_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["content"].label = ""
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Report",
                FloatingField("title"),
                Div(
                    Div("pub_date", css_class="col-12 col-xl-6"),
                    Div("slug", css_class="col-12 col-xl-6"),
                    css_class="row mt-4",
                ),
                css_class="mt-4",
            ),
            Fieldset(
                "Content",
                "content",
                css_class="mt-4",
            ),
            Fieldset(
                "Privacy",
                "privacy",
                css_class="mt-4",
            ),
        )

        if self.instance.pk:
            self.helper.add_input(
                Submit("submit", "Update report", css_class="btn-lg w-100 mt-4")
            )
        else:
            self.helper.add_input(
                Submit("submit", "Create report", css_class="btn-lg w-100 mt-4")
            )

    def clean_slug(self):
        """Check that the user does not have another slug with the same value"""
        slug = self.cleaned_data.get("slug")
        try:
            tr = TripReport.objects.get(user=self.user, slug=slug)
            if tr == self.instance:
                return slug
            raise ValidationError("The slug must be unique.")
        except TripReport.DoesNotExist:
            return slug


class TripForm(DistanceUnitFormMixin, forms.ModelForm):
    class Meta:
        model = Trip
        fields = [
            "cave_name",
            "cave_region",
            "cave_country",
            "cave_url",
            "start",
            "end",
            "type",
            "privacy",
            "clubs",
            "expedition",
            "cavers",
            "horizontal_dist",
            "vert_dist_down",
            "vert_dist_up",
            "surveyed_dist",
            "resurveyed_dist",
            "aid_dist",
            "notes",
        ]
        widgets = {
            "start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].label = ""
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Cave details",
                Div(
                    Div("cave_name", css_class="col-12"),
                    Div("cave_region", css_class="col-12 col-lg-6"),
                    Div("cave_country", css_class="col-12 col-lg-6"),
                    Div("cave_url", css_class="col-12"),
                    css_class="row",
                ),
            ),
            Fieldset(
                "Trip details",
                Div(
                    Div("start", css_class="col-12 col-lg-6"),
                    Div("end", css_class="col-12 col-lg-6"),
                    Div("type", css_class="col-12 col-lg-6"),
                    Div("privacy", css_class="col-12 col-lg-6"),
                    Div("clubs", css_class="col-12 col-lg-6"),
                    Div("expedition", css_class="col-12 col-lg-6"),
                    Div("cavers", css_class="col"),
                    css_class="row",
                ),
                css_class="mt-4",
            ),
            Fieldset(
                "Distances",
                HTML(
                    """
<p class="text-muted mb-4">
    The unit of measurement must be entered in the field, for
    example <code>500ft</code> or <code>150m</code>. Distances recorded are counted
    towards your overall statistics, unless they are added to a 'Surface' trip, in
    which case they will be ignored. Supported units: <code>m km cm ft yd
    inch mi furlong</code>.
</p>
                """
                ),
                Div(
                    Div("horizontal_dist", css_class="col"),
                    Div("vert_dist_down", css_class="col"),
                    Div("vert_dist_up", css_class="col"),
                    Div("surveyed_dist", css_class="col"),
                    Div("resurveyed_dist", css_class="col"),
                    Div("aid_dist", css_class="col"),
                    css_class="row row-cols-1 row-cols-lg-3",
                ),
                css_class="mt-4",
            ),
            Fieldset(
                "Trip notes",
                "notes",
                css_class="mt-4",
            ),
        )

        if self.instance.pk:
            self.helper.add_input(
                Submit("submit", "Update trip", css_class="btn-lg w-100 mt-4")
            )
        else:
            self.helper.add_input(
                Submit("submit", "Create trip", css_class="btn-lg w-100 mt-4")
            )
            self.helper.add_input(
                Submit(
                    "addanother",
                    "Create and add another",
                    css_class="btn-secondary btn-lg w-100 mt-3",
                )
            )

    def clean_start(self):
        """Validate the trip start date/time"""
        # Trips must not start more than a week in the future.
        one_week_from_now = timezone.now() + timedelta(days=7)
        if self.cleaned_data.get("start") > one_week_from_now:
            raise ValidationError(
                "Trips must not start more than one week in the future."
            )
        return self.cleaned_data["start"]

    def clean_end(self):
        """Validate the trip end date/time"""
        # Trips must not end more than 31 days in the future.
        end = self.cleaned_data.get("end")
        if end:
            one_month_from_now = timezone.now() + timedelta(days=31)
            if end > one_month_from_now:
                raise ValidationError(
                    "Trips must not end more than 31 days in the future."
                )
        return end

    def clean(self):
        """Validate relations between the start/end datetimes"""
        super().clean()

        start = self.cleaned_data.get("start")
        end = self.cleaned_data.get("end")

        if end and start:
            length = end - start
            if end == start:
                self.add_error(
                    "end",
                    "The start and end time must not be the same. If you "
                    "do not know the end time, leave it blank.",
                )
            elif start > end:
                self.add_error(
                    "start", "The trip start time must be before the trip end time."
                )
            elif length > timedelta(days=60):
                self.add_error(
                    "end",
                    "The trip is unrealistically long in duration (over 60 days).",
                )


class AllUserNotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["message", "url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("notify", "Send Notification"))


class TripSearchForm(forms.Form):
    terms = forms.CharField(
        label="Terms",
        required=True,
        help_text="Text to search for in trip records.",
    )
    user = forms.CharField(
        label="Username",
        required=False,
        help_text="Limit search to a specific user (optional).",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.form_action = reverse("log:search_results")
        self.helper.layout = Layout(
            Div(
                Field("terms", wrapper_class="col-12 col-lg-8"),
                Field("user", wrapper_class="col-12 col-lg-4"),
                css_class="row",
            ),
            Submit("submit", "Search", css_class="btn btn-primary w-100 mt-3"),
        )

    def clean_terms(self):
        terms = self.cleaned_data.get("terms").strip()
        if len(terms) < 3:
            raise ValidationError("Please enter at least three characters.")
        return terms

    def clean_user(self):
        user = self.cleaned_data.get("user").strip()
        if user:
            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                raise ValidationError("Username not found.")
        return user


# TODO: Refactor comments
# class AddCommentForm(forms.Form):
#     content = forms.CharField(
#         help_text="Your comment will be visible to anyone who can view this page.",
#         widget=forms.Textarea(attrs={"rows": 4}),
#     )
#     type = forms.CharField(widget=forms.HiddenInput())
#     pk = forms.IntegerField(widget=forms.HiddenInput())

#     def __init__(self, request, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.request = request

#         self.helper = FormHelper()
#         self.helper.form_method = "post"
#         self.helper.form_class = ""
#         self.helper.form_show_errors = False
#         self.helper.form_show_labels = False
#         self.helper.form_action = reverse("log:comment_add")
#         self.helper.add_input(Submit("submit", "Add comment"))

#     def clean_type(self):
#         type = self.cleaned_data.get("type")
#         if type == "trip":
#             self.type_str = "trip"
#             return Trip
#         elif type == "tripreport":
#             self.type_str = "trip report"
#             return TripReport
#         else:
#             raise ValidationError(
#                 "You are not allowed to comment on that type of item."
#             )

#     def clean_content(self):
#         content = self.cleaned_data.get("content")
#         if len(content) > 2000:
#             raise ValidationError(
#                 "Your comment must be less than 2000 characters long."
#             )
#         return content

#     def clean(self):
#         cleaned_data = super().clean()
#         type = cleaned_data.get("type")
#         pk = cleaned_data.get("pk")

#         if not type or not pk:
#             raise ValidationError("Invalid form data.")

#         try:
#             self.object = type.objects.get(pk=pk)
#         except (Trip.DoesNotExist, TripReport.DoesNotExist):
#             raise ValidationError("The item you wish to comment on does not exist.")

#         if not self.object.is_viewable_by(self.request.user):
#             raise ValidationError("You are not allowed to comment on that item.")

#         if not self.object.user.allow_comments:
#             raise ValidationError("Comments are not allowed on that item.")

#         return self.cleaned_data

#     def save(self, commit=True):
#         content = self.cleaned_data.get("content")
#         new = Comment.objects.create(
#             content_object=self.object, author=self.request.user, content=content
#         )
#         if commit:
#             new.save()
#         return new
