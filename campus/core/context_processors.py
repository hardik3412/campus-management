def notifications_processor(request):
    if request.user.is_authenticated:
        return {
            'notifications': request.user.notifications.filter(is_read=False).order_by('-created_at')
        }
    return {}
