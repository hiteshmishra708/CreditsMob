from app.models import User
#comment to checck commits

def create_or_get_user(udid):
    if not udid:
        return
    user = User.objects.get(udid=udid)
    if not user:
        user = User()
        user.udid = udid
        user.save()
    return user


