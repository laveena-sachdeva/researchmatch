"""Template tags for the ``conversation`` app."""
from django.contrib.auth import get_user_model
from django.template import Library
from django.template.defaultfilters import truncatechars

from ..models import BlockedUser

register = Library()

@register.simple_tag(name='chain_user_names')
def chain_user_names(users, exclude_user, truncate=35):
    """Tag to return a truncated chain of user names."""
    if not users or not isinstance(exclude_user, get_user_model()):
        return ''
    return truncatechars(
        ', '.join(u'{}'.format(u) for u in users.exclude(pk=exclude_user.pk)),
        truncate)


@register.simple_tag(name='is_blocked')
def is_blocked(blocked_by, user):
    if (not isinstance(blocked_by, get_user_model()) or not
            isinstance(user, get_user_model())):
        return False
    try:
        return BlockedUser.objects.get(blocked_by=blocked_by, user=user)
    except BlockedUser.DoesNotExist:
        return False


@register.simple_tag(name='get_last_message')
def get_last_message(conversation):
    try:
        return conversation.messages.order_by('-date')[0]
    except IndexError:
        return None

@register.simple_tag(name='get_other_user')
def get_other_user(conversation,exclude_user):
    try:
        return conversation.users.exclude(pk=exclude_user.pk)[0].username
    except:
        return None