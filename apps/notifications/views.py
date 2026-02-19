from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notifications.models import Activity


@login_required
def notifications_list(request):
    """show all notifications for the logged-in user"""
    notifications = Activity.objects.filter(recipient=request.user).selected_related(
        "actor"
    )

    notifications.filter(is_read=False).update(is_read=True)

    return render(
        request,
        "notifications/notifications_list.html",
        {"notifications": notifications},
    )


@login_required
def mark_notification_read(request, notification_id):
    """mark a single notification as read"""
    notification = get_object_or_404(
        Activity, id=notification_id, recipient=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect("notifications:notifications_list")
