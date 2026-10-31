"""Bell count on every page (docs/04 Layout, C-11)."""


def unread_count(request):
    """Number of unread notifications for the top bar bell; one small query per page."""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {}
    return {"unread_count": user.notifications.filter(is_read=False).count()}
