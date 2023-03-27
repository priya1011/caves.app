from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model
from logger.models import Trip


class PublicViewsIntegrationTests(TestCase):
    def setUp(self):
        # Reduce log level to avoid 404 error
        import logging

        logger = logging.getLogger("django.request")
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        self.client = Client()

        # Create a test user
        self.user = get_user_model().objects.create_user(
            email="test@user.app",
            password="password",
            username="testuser",
            first_name="Test",
            last_name="User",
        )
        self.user.bio = "This is my bio."
        self.user.is_active = True
        self.user.privacy = get_user_model().PUBLIC
        self.user.save()

        # Iterate and create several trips belonging to the user
        for i in range(1, 11):
            start = timezone.make_aware(
                timezone.datetime(year=timezone.now().year, month=i, day=1)
            )
            end = start + timezone.timedelta(hours=5)
            self.user.trip_set.create(
                cave_name=f"Trip {i}",
                start=start,
                end=end,
                privacy=Trip.DEFAULT,
                vert_dist_up="100m",
            )

    def tearDown(self):
        """Reset the log level back to normal"""
        import logging

        logger = logging.getLogger("django.request")
        logger.setLevel(self.previous_level)

    def test_public_user_profile_accessible(self):
        """Test that the user profile page loads"""
        self.user.privacy = get_user_model().PUBLIC
        self.user.save()
        response = self.client.get(f"/u/{self.user.username}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.full_name)
        self.assertContains(response, self.user.bio)

        # Test that the user's trips are listed
        for trip in self.user.trip_set.all():
            self.assertContains(response, trip.cave_name)

    def test_user_profile_private(self):
        """Test that the user profile page is not accessible if the user is private"""
        self.user.privacy = get_user_model().PRIVATE
        self.user.save()
        response = self.client.get(f"/u/{self.user.username}/")
        self.assertEqual(response.status_code, 404)

    def test_default_privacy_trip_not_accessible_for_private_user(self):
        """Test that a trip belonging to a private user is not accessible"""
        self.user.privacy = get_user_model().PRIVATE
        self.user.save()
        trip = self.user.trip_set.first()
        trip.privacy = Trip.DEFAULT
        trip.save()
        response = self.client.get(f"/u/{self.user.username}/{trip.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_public_trip_for_private_user_is_accessible(self):
        """Test that a public trip belonging to a private user is accessible"""
        self.user.privacy = get_user_model().PRIVATE
        self.user.save()
        trip = self.user.trip_set.first()
        trip.privacy = Trip.PUBLIC
        trip.save()
        response = self.client.get(f"/u/{self.user.username}/{trip.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, trip.cave_name)

    def test_private_trip_for_public_user_is_not_accessible(self):
        """Test that a private trip belonging to a public user is not accessible"""
        self.user.privacy = get_user_model().PUBLIC
        self.user.save()
        trip = self.user.trip_set.first()
        trip.privacy = Trip.PRIVATE
        trip.save()
        response = self.client.get(f"/u/{self.user.username}/{trip.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_incorrect_username_slug_for_valid_trip_returns_404(self):
        """Test that a url with an incorrect username slug returns a 404"""
        trip = self.user.trip_set.first()
        trip.privacy = Trip.PUBLIC
        trip.save()
        response = self.client.get(f"/u/invalid-user/{trip.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_user_profile_without_bio_or_trips(self):
        """Test that the user profile page loads if the user has no bio or trips"""
        self.user.privacy = get_user_model().PUBLIC
        self.user.bio = ""
        self.user.save()
        self.user.trip_set.all().delete()
        response = self.client.get(f"/u/{self.user.username}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.full_name)
        self.assertContains(
            response,
            "This is the public profile of a caves.app user who has not added any trips or a bio yet.",
        )

    def test_show_statistics_user_setting(self):
        """Test that the user profile page shows statistics if the user has the setting enabled"""
        self.user.privacy = get_user_model().PUBLIC
        self.user.show_statistics = True
        self.user.profile_page_title = ""
        self.user.save()
        response = self.client.get(f"/u/{self.user.username}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.full_name)
        self.assertContains(response, self.user.bio)

        # Test that the user's trips are listed
        for trip in self.user.trip_set.all():
            self.assertContains(response, trip.cave_name)

        # Test that the statistics are shown
        self.assertContains(response, "Total trips")
        self.assertContains(response, "Rope ascent")
        self.assertContains(response, "Aid climbed")

        # Test that the statistics are not shown if diabled
        self.user.show_statistics = False
        self.user.save()
        response = self.client.get(f"/u/{self.user.username}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.full_name)
        self.assertContains(response, self.user.bio)

        # Test that the user's trips are listed
        for trip in self.user.trip_set.all():
            self.assertContains(response, trip.cave_name)

        # Test that the statistics are not shown
        self.assertNotContains(response, "Total trips")
        self.assertNotContains(response, "Rope ascent")
        self.assertNotContains(response, "Aid climbed")

    def test_custom_profile_page_title(self):
        """Test that the user profile page uses the custom title if set"""
        self.user.privacy = get_user_model().PUBLIC
        self.user.save()
        self.user.profile_page_title = "This is my custom title"
        self.user.save()
        response = self.client.get(f"/u/{self.user.username}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.profile_page_title)

    def test_private_notes(self):
        """Test that notes are not shown on public trip pages if the user has notes set to private"""
        trip = self.user.trip_set.first()
        trip.privacy = Trip.PUBLIC
        trip.notes = "This is a note."
        trip.save()

        # Test that the notes are not shown if the user has notes set to private
        self.user.private_notes = True
        self.user.save()
        response = self.client.get(f"/u/{self.user.username}/{trip.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, trip.cave_name)
        self.assertNotContains(response, trip.notes)

        # Test that the notes are shown if the user has notes set to public
        self.user.private_notes = False
        self.user.save()
        response = self.client.get(f"/u/{self.user.username}/{trip.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, trip.cave_name)
        self.assertContains(response, trip.notes)

    def test_statistics_show_in_correct_units_for_user(self):
        """Test that the statistics on the user profile page are shown in the correct units"""
        self.user.privacy = get_user_model().PUBLIC
        self.user.show_statistics = True
        self.user.profile_page_title = "Testing statistics unit function"
        self.user.units = get_user_model().METRIC
        self.user.save()

        # Test that the statistics are shown in the correct metric units
        response = self.client.get(f"/u/{self.user.username}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.profile_page_title)
        self.assertContains(response, "1000m")

        # Test that the statistics are shown in the correct imperial units
        self.user.units = get_user_model().IMPERIAL
        self.user.save()
        response = self.client.get(f"/u/{self.user.username}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.profile_page_title)
        self.assertContains(response, "3281ft")
