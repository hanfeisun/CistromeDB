from django.conf import settings
from django.contrib.auth.models import User, check_password

# Use hashlib module if for Python 2.5+, fall back on old sha and md5 modules
# sha1 requires explicit calls to new if also being passed to hmac (!)
try:
    import hashlib
    sha1 = hashlib.sha1
    sha = sha1
    md5 = hashlib.md5
except ImportError, e:
    from sha import new as sha1
    import sha
    from md5 import new as md5

from datacollection.models import CistromeUser


def new_secure_hash( text_type=None ):
    """
    Returns either a sha1 hash object (if called with no arguments), or a
    hexdigest of the sha1 hash of the argument `text_type`.
    """
    if text_type:
        return sha1( text_type ).hexdigest()
    else:
        return sha1()



def check_password(cistrome_user, password):
    if cistrome_user.password == new_secure_hash(password):
        return True
    else:
        return None

class CistromeAuthBackend(object):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name, and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'sha1$4e987$afbcf42e21bd417fb71db8c66b321e9fc33051de'
    """

    def authenticate(self, username=None, password=None):
        try:
            cistrome_user = CistromeUser.objects.get(email=username)

        except CistromeUser.DoesNotExist:
            return  None


        pwd_valid = check_password(cistrome_user, password)
        if pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked; the password
                # from settings.py will.
                user = User(username=username, password='get from cistromeap')
                user.is_staff = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None