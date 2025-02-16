import humanize
from django.contrib.auth import get_user_model
from django.contrib.gis.measure import D, Distance
from django.db.models import Count
from django.utils import timezone

from .models import Trip

User = get_user_model()


def sort_comma_separated_list(qs, value, limit=10):
    """Sort a field that has a comma separated list of values from a QuerySet"""
    if not bool(qs):
        return None

    values = qs.values(value)
    common = {}
    for v in values:
        split_list = v[value].split(",")
        for split_value in split_list:
            trimmed = split_value.strip()
            if not trimmed:
                continue
            if trimmed in common:
                common[trimmed] += 1
            else:
                common[trimmed] = 1
    return sorted(common.items(), key=lambda x: x[1], reverse=True)[0:limit]


def stats_for_user(qs, year=None):  # noqa C901
    """Get statistics of trips within a QuerySet, optionally by year"""
    if year:
        qs = qs.filter(start__year=year)

    # Initialise results
    results = {
        "vert_down": Distance(m=0),
        "vert_up": Distance(m=0),
        "surveyed": Distance(m=0),
        "resurveyed": Distance(m=0),
        "aided": Distance(m=0),
        "horizontal": Distance(m=0),
        "trips": 0,
        "time": timezone.timedelta(0),
    }

    # Return the empty results if there are no trips.
    if not bool(qs):
        results["time"] = "0"
        return results

    # Iterate and add up
    for trip in qs:
        if trip.type == Trip.SURFACE:
            continue  # Don't count surface trips
        results["trips"] += 1
        results["time"] += trip.duration if trip.end else timezone.timedelta(0)
        results["vert_down"] += trip.vert_dist_down
        results["vert_up"] += trip.vert_dist_up
        results["surveyed"] += trip.surveyed_dist
        results["resurveyed"] += trip.resurveyed_dist
        results["horizontal"] += trip.horizontal_dist
        results["aided"] += trip.aid_dist

    # Humanise duration
    results["time"] = humanize.precisedelta(
        results["time"], minimum_unit="hours", format="%.0f"
    )

    return results


def common_caves(qs, limit=10):
    """Get a list of the most common caves in a QuerySet"""
    if not bool(qs):
        return None

    return (
        qs.values("cave_name")
        .annotate(count=Count("cave_name"))
        .order_by("-count")[0:limit]
    )


def common_cavers(qs, limit=10):
    """Get a list of the most common cavers in a QuerySet, by trip count"""
    return sort_comma_separated_list(qs, "cavers", limit)


def common_cavers_by_time(qs, limit=10):
    """Get a list of the most common cavers in a QuerySet, by time"""
    if not bool(qs):
        return None

    cavers = {}
    for trip in qs:
        if not trip.cavers:
            continue
        split_list = trip.cavers.split(",")
        for caver in split_list:
            caver = caver.strip()
            if caver in cavers and trip.end:
                cavers[caver] += trip.duration
            elif trip.end:
                cavers[caver] = trip.duration

    sorted_dict = sorted(cavers.items(), key=lambda x: x[1], reverse=True)[0:limit]
    humanised = {}
    for k, v in sorted_dict:
        humanised[k] = humanize.precisedelta(v, minimum_unit="minutes", format="%.0f")
    return humanised.items()


def common_clubs(qs, limit=10):
    """Get a list of the most common clubs in a QuerySet"""
    return sort_comma_separated_list(qs, "clubs", limit)


def common_types(qs, limit=10):
    """Get a list of the most common types in a QuerySet"""
    if not bool(qs):
        return None

    return qs.values("type").annotate(count=Count("type")).order_by("-count")[0:limit]


def vertical_and_horizontal_count(qs):
    """Get the number of trips with vertical and horizontal distance"""
    if not bool(qs):
        return None

    vertical, horizontal = 0, 0
    for trip in qs:
        if trip.vert_dist_up or trip.vert_dist_down or trip.aid_dist:
            vertical += 1
        else:
            horizontal += 1
    return vertical, horizontal


def trip_averages(qs, units):  # noqa C901
    """Get the average distances in a QuerySet"""
    if not bool(qs):
        return None

    results = {
        "Rope climbed per trip": Distance(m=0),
        "Rope descended per trip": Distance(m=0),
        "Surveyed per trip": Distance(m=0),
        "Resurveyed per trip": Distance(m=0),
        "Aid climbed per trip": Distance(m=0),
        "Horizontal distance per trip": Distance(m=0),
        "Time underground per trip": timezone.timedelta(0),
    }
    survey_trips, survey_hours, vert_trips, vert_hours = 0, 0, 0, 0
    for trip in qs:
        results["Time underground per trip"] += (
            trip.duration if trip.end else timezone.timedelta(0)
        )
        results["Rope climbed per trip"] += (
            trip.vert_dist_up if trip.vert_dist_up else D()
        )
        results["Rope descended per trip"] += (
            trip.vert_dist_down if trip.vert_dist_down else D()
        )
        results["Surveyed per trip"] += (
            trip.surveyed_dist if trip.surveyed_dist else D()
        )
        results["Resurveyed per trip"] += (
            trip.resurveyed_dist if trip.resurveyed_dist else D()
        )
        results["Aid climbed per trip"] += trip.aid_dist if trip.aid_dist else D()
        results["Horizontal distance per trip"] += (
            trip.horizontal_dist if trip.horizontal_dist else D()
        )
        if trip.surveyed_dist > D(0) or trip.resurveyed_dist > D(0):
            survey_trips += 1
            if trip.duration:
                survey_hours += trip.duration.total_seconds() / 3600
        if trip.vert_dist_up > D() or trip.vert_dist_down > D() or trip.aid_dist > D():
            vert_trips += 1
            if trip.duration:
                vert_hours += trip.duration.total_seconds() / 3600

    # Store some results for later use in 'per hour' calculations
    climbed = results["Rope climbed per trip"]
    descended = results["Rope descended per trip"]
    surveyed = results["Surveyed per trip"]
    resurveyed = results["Resurveyed per trip"]
    total_survey = results["Surveyed per trip"] + results["Resurveyed per trip"]
    if results["Time underground per trip"]:
        total_hours = results["Time underground per trip"].total_seconds() / 3600
    else:
        total_hours = None

    # All the results so far are 'per trip' so divide by count of trips.
    for key, value in results.items():
        if value:
            results[key] = value / qs.count()

    # This could be optimised but at least this ensures no division by zero.
    if climbed and total_hours:
        results["Rope climbed per hour"] = climbed / total_hours
    if descended and total_hours:
        results["Rope descended per hour"] = descended / total_hours
    if climbed and vert_hours:
        results["Rope climbed per hour*"] = climbed / vert_hours
    if descended and vert_hours:
        results["Rope descended per hour*"] = descended / vert_hours
    if total_survey and survey_hours:
        results["Surveyed** per hour***"] = total_survey / survey_hours
    if surveyed and total_hours:
        results["Surveyed per hour"] = surveyed / total_hours
    if resurveyed and total_hours:
        results["Resurveyed per hour"] = resurveyed / total_hours
    if total_survey and survey_hours:
        results["Surveyed** per hour***"] = total_survey / survey_hours
    if climbed and vert_trips:
        results["Rope climbed per trip*"] = climbed / vert_trips
    if descended and vert_trips:
        results["Rope descended per trip*"] = descended / vert_trips
    if surveyed and survey_trips:
        results["Surveyed per trip***"] = surveyed / survey_trips
    if total_survey and survey_trips:
        results["Surveyed** per trip***"] = total_survey / survey_trips

    # Process the results for display in humanised time and user specified units
    processed_results = {}
    for key, value in results.items():
        if value:
            if type(value) == timezone.timedelta:
                value = humanize.precisedelta(
                    value, minimum_unit="minutes", format="%.0f"
                )
            elif type(value) == Distance:
                if units == User.IMPERIAL:
                    processed_results[key] = f"{round(value.ft, 2)}ft"
                else:
                    processed_results[key] = f"{round(value.m, 2)}m"

    # Calculate trips per week
    first_trip = qs.order_by("start").first().start
    last_trip = qs.order_by("-start").first().start
    weeks = (last_trip - first_trip).days / 7
    if first_trip.date() != last_trip.date() and weeks != 0:
        processed_results["Trips per week"] = round(qs.count() / weeks, 2)

    return sorted(processed_results.items())
