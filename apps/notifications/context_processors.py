from notifications.models import Activity


def unread_notifications(request):
    if request.user.is_authenticated:
        unread_count = Activity.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return {"unread_count": unread_count}
    return {"unread_count": 0}
