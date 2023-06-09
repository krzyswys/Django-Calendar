from calendar_events.models import Events, EventCategories, EventOccurrences
from django.db.models import Sum, Count


def calculate_event_duration_by_category(start_date=None, end_date=None):
    result = {}
    categories = (
        Events.objects.order_by().values_list("event_category", flat=True).distinct()
    )
    event_categories = EventCategories.objects.filter(event_category_id__in=categories)
    events = Events.objects.all()
    events_occurencies = EventOccurrences.objects.all()

    if start_date:
        events = events.filter(start_time__gte=start_date)
        events_occurencies = events_occurencies.filter(start_time__gte=start_date)

    if end_date:
        events = events.filter(end_time__lte=end_date)
        events_occurencies = events_occurencies.filter(end_time__lte=end_date)

    for category in event_categories:
        duration_sum = events.filter(event_category=category).aggregate(
            duration_sum=Sum("duration")
        )["duration_sum"]
        duration_sum_occurence = events_occurencies.filter(
            event_category=category
        ).aggregate(duration_sum=Sum("duration"))["duration_sum"]
        result[category.name] = duration_sum + duration_sum_occurence

    return result


def calculate_event_duration_by_priority(start_date=None, end_date=None):
    result = {}
    priorities = (
        Events.objects.order_by()
        .values_list("priority_level__priority_value", flat=True)
        .distinct()
    )
    events = Events.objects.all()
    events_occurencies = EventOccurrences.objects.all()

    if start_date:
        events = events.filter(start_time__gte=start_date)
        events_occurencies = events_occurencies.filter(start_time__gte=start_date)

    if end_date:
        events = events.filter(end_time__lte=end_date)
        events_occurencies = events_occurencies.filter(end_time__lte=end_date)
    for priority in priorities:
        duration_sum = events.filter(priority_level__priority_value=priority).aggregate(
            duration_sum=Sum("duration")
        )["duration_sum"]
        duration_sum_occurence = events_occurencies.filter(
            priority_level__priority_value=priority
        ).aggregate(duration_sum=Sum("duration"))["duration_sum"]
        result[priority] = duration_sum + duration_sum_occurence

    return result


def calculate_location_stats(start_date=None, end_date=None):
    events = Events.objects.all()
    events_occurencies = EventOccurrences.objects.all()

    if start_date:
        events = events.filter(start_time__gte=start_date)
        events_occurencies = events_occurencies.filter(start_time__gte=start_date)

    if end_date:
        events = events.filter(end_time__lte=end_date)
        events_occurencies = events_occurencies.filter(end_time__lte=end_date)

    total_events = events.count() + events_occurencies.count()
    location_stats = (
        events.values("localization")
        .annotate(count=Count("localization"))
        .order_by("-count")
    )
    location_stats_for_occurences = (
        events_occurencies.values("localization")
        .annotate(count=Count("localization"))
        .order_by("-count")
    )
    combined_stats = {}
    for loc in location_stats:
        combined_stats[loc["localization"]] = round(
            (loc["count"] / total_events) * 100, 2
        )

    for loc in location_stats_for_occurences:
        if loc["localization"] in combined_stats:
            combined_stats[loc["localization"]] += round(
                (loc["count"] / total_events) * 100, 2
            )
        else:
            combined_stats[loc["localization"]] = round(
                (loc["count"] / total_events) * 100, 2
            )
    return combined_stats


def calculate_priority_stats(start_date=None, end_date=None):
    events = Events.objects.all()
    events_occurencies = EventOccurrences.objects.all()
    if start_date:
        events = events.filter(start_time__gte=start_date)
        events_occurencies = events_occurencies.filter(start_time__gte=start_date)

    if end_date:
        events = events.filter(end_time__lte=end_date)
        events_occurencies = events_occurencies.filter(end_time__lte=end_date)

    total_events = events.count() + events_occurencies.count()
    priority_stats = (
        events.values("priority_level__priority_value")
        .annotate(count=Count("priority_level__priority_value"))
        .order_by("-priority_level__priority_value")
    )
    priority_stats_occurences = (
        events_occurencies.values("priority_level__priority_value")
        .annotate(count=Count("priority_level__priority_value"))
        .order_by("-priority_level__priority_value")
    )

    combined_stats = {}
    for p in priority_stats:
        combined_stats[p["priority_level__priority_value"]] = round(
            (p["count"] / total_events) * 100, 2
        )

    for p in priority_stats_occurences:
        if p["priority_level__priority_value"] in combined_stats:
            combined_stats[p["priority_level__priority_value"]] += round(
                (p["count"] / total_events) * 100, 2
            )
        else:
            combined_stats[p["priority_level__priority_value"]] = round(
                (p["count"] / total_events) * 100, 2
            )
    return combined_stats
    # return {
    #     p["priority_level__priority_value"]: round((p["count"] / total_events) * 100, 2)
    #     for p in priority_stats
    # }
