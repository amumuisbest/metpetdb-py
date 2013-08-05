import base64
import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.models import Group
from django.db import transaction

from .models import User as MetpetUser
from .models import Group, GroupExtra, GroupAccess

def translate(raw_crypt):
    """Translates a metpetdb salted password into a Django salted password."""
    logger.debug("Re-crypting %s.", repr(raw_crypt))
    if len(raw_crypt) == 0:
        return 'sha1$$' # Unusuable password
    salt_length = raw_crypt[0]
    raw_salt = raw_crypt[1:salt_length+1]
    raw_hash = raw_crypt[salt_length+1:]
    cooked_salt = base64.b64encode(raw_salt)
    cooked_hash = base64.b16encode(raw_hash).lower() # NB: Base16 = hex
    # XXX: 'sha1-b64-salt' is nonstandard, but there's no obvious alternative.
    cooked_crypt = 'sha1-b64-salt${}${}'.format(cooked_salt, cooked_hash)
    return cooked_crypt


@transaction.commit_on_success
def main():
    """Imports metpetdb's user table into Django, for use with the auth system.
    
    BEFORE RUNNING THIS SCRIPT, execute the following SQL:

        ALTER TABLE users ADD COLUMN django_user_id int UNIQUE REFERENCES
        auth_user(id); 
    """
    for metpet_user in MetpetUser.objects.filter(django_user=None):
        logger.info("Transitioning %s.", metpet_user.name)
        email = metpet_user.email
        logger.debug("Email = %s", email)
        # Use the email for the username, but strip out disallowed characters
        # and cap total length at 30 characters to comply with Django's 
        # requirements:
        username = ''.join(c for c in email if c.isalnum() or c in ['_', '@',
                                                                    '+', '.',
                                                                    '-'])[:30]
        logger.debug("Username = %s", username)
        password = translate(bytearray(metpet_user.password))
        logger.debug("Password hash = %s", password)
        result = AuthUser(username=username, password=password, email=email,
                          is_staff=False, is_active=True, is_superuser=False)
        result.save()
        metpet_user.django_user = result
        metpet_user.save()
        if metpet_user.enabled.upper() == 'Y':
            # Add user to public group(s), so (s)he can read public things
            metpet_user.auto_verify(None) # Pass None to skip code check
        if metpet_user.contributor_enabled.upper() == 'Y':
            # Add user to personal group, so (s)he can create things
            metpet_user.manual_verify()
        metpet_user.save()