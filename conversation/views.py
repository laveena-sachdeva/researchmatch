"""Views for the ``conversation`` app."""
import collections

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic import (
    CreateView,
    DetailView,
    RedirectView,
    TemplateView,
    UpdateView,
)

from django_libs.loaders import load_member
from django_libs.utils.email import send_email
from django_libs.views_mixins import AjaxResponseMixin

from .forms import MessageForm
from .models import BlockedUser, Conversation

def int_str(val, keyspace):
    """ Turn a positive integer into a string. """
    assert val >= 0
    out = ""
    while val > 0:
        val, digit = divmod(val, len(keyspace))
        out += keyspace[digit]
    return out[::-1]

def str_int(val, keyspace):
    """ Turn a string into a positive integer. """
    out = 0
    for c in val:
        out = out * len(keyspace) + keyspace.index(c)
    return out

keyspace = "fw59eorpma2nvxb07liqt83_u6kgzs41-ycdjh"

class ConversationViewMixin(AjaxResponseMixin):
    """Mixin for conversation related views."""
    model = Conversation

    def get_form_class(self):
        print("Get Form Class")

        if hasattr(settings, 'CONVERSATION_MESSAGE_FORM'):
            return load_member(settings.CONVERSATION_MESSAGE_FORM)
        return MessageForm

    def get_form_kwargs(self, *args, **kwargs):
        print("Get Form Kwargs")

        kwargs = super(ConversationViewMixin, self).get_form_kwargs(
            *args, **kwargs)

        kwargs.update({
            'user': self.user,
            'conversation': self.object,
            'instance': None,
            'initial_user': self.initial_user if hasattr(
                self, 'initial_user') else None,
        })

        return kwargs

    def get_context_data(self,**kwargs):
        print("Get context data")

        ctx = super(ConversationViewMixin, self).get_context_data(**kwargs)
        conversations = {}
        for conversation in Conversation.objects.filter(
                users__in=[self.request.user]).exclude(
                archived_by__in=[self.request.user]):
            try:
                latest_message = conversation.messages.first().date.strftime(
                    '%Y-%m-%d')
                conversations['{}-{}'.format(
                    latest_message, conversation.pk)] = conversation
            except AttributeError:
                continue
        ctx.update({
            'conversations': collections.OrderedDict(
                reversed(sorted(conversations.items()))),
            'initial_user':self.initial_user if hasattr(
                self, 'initial_user') else None})
        print("End context data")
        return ctx

    def get_success_url(self):
        # Send instant notifications
        print("Get success url")

        if (not hasattr(settings, 'CONVERSATION_ENABLE_NOTIFICATIONS') or
                settings.CONVERSATION_ENABLE_NOTIFICATIONS):
            for user in self.object.users.exclude(pk=self.user.pk):
                if (hasattr(user, 'disable_conversation_notifications') and
                        user.disable_conversation_notifications):
                    continue
                send_email(
                    None,
                    {
                        'user': user,
                        'conversations': [self.object],
                    },
                    'conversation/email/message_digest_subject.html',
                    'conversation/email/message_digest_body.html',
                    # settings.FROM_EMAIL,
                    self.user.email,
                    recipients=[user.email, ],
                    priority='medium',
                )
                self.object.notified.add(user)
        print("before redirecting")
        print(self.request)
        self.request.session['_old_post'] = self.request.POST
        return reverse('conversation_update', kwargs={'pk': 999})


class ConversationUpdateView(ConversationViewMixin, UpdateView):
    model = Conversation
    def get_object(self, queryset=None):
        obj = super(ConversationUpdateView, self).get_object(queryset=queryset)
        if obj is None:
            raise Http404("Job doesn't exists")
        return obj
    """View to update a conversation."""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        print("conversation update dispatch")
        old_post = request.session.get('_old_post')
        if request.method == "POST":
            old_post = request.POST
        print(old_post)
        self.user = request.user
        try: 
            initial_user_id = old_post['other_user_id']
                
            print("initial_user_id")
            print(initial_user_id)
            print(request.POST)
            self.initial_user = get_user_model().objects.get(
                pk=initial_user_id)
        except get_user_model().DoesNotExist:
            print("or here?")
            raise Http404
        print("is our here?")
        print(self.initial_user)

        # Fecth the existing conversation of these users
        conversations = self.user.conversations.filter(pk__in=self.initial_user.conversations.values_list('pk'))
        self.kwargs = {'pk': conversations[0].pk}

        self.object = self.get_object(conversations)
        print(self.object)
        print(conversations)
        # initial_user_id = request.POST.get('other_user_id')
        # If conversation has been read by all participants
        if self.object.unread_by.count() == 0:
            self.object.read_by_all = now()
            self.object.save()
        print("request")
        print(request)
        return super(ConversationUpdateView, self).dispatch(
            request, *args, **kwargs)


class ConversationCreateView(ConversationViewMixin, CreateView):
    """View to start a new conversation."""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        print("conversation create dispatch")
        self.user = request.user

        try:
            initial_user_id = request.POST.get('other_user_id')
            print("initial_user_id")
            print(initial_user_id)
            self.initial_user = get_user_model().objects.get(
                pk=initial_user_id)
        except get_user_model().DoesNotExist:
            print("is this one raised?")
            raise Http404
        # Check for an existing conversation of these users
        conversations = self.user.conversations.filter(pk__in=self.initial_user.conversations.values_list('pk'))
        if conversations:
            print(conversations)
            request.session['_old_post'] = request.POST
            return HttpResponseRedirect(reverse(
                'conversation_update', kwargs={'pk': 999}))
            # return HttpResponseRedirect(reverse('conversation_update'))
        return super(ConversationCreateView, self).dispatch(
            request, {'pk': initial_user_id},  kwargs={'pk': initial_user_id})


class ConversationListView(TemplateView):
    """View to list all conversations of a user."""
    template_name = 'conversation/conversation_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        active_conversations = request.user.conversations.exclude(
            archived_by__in=[request.user])
        if active_conversations:
            return HttpResponseRedirect(reverse('conversation_update', kwargs={
                'pk': active_conversations[0].pk}))
        return super(ConversationListView, self).dispatch(
            request, *args, **kwargs)


class ConversationTriggerView(DetailView):
    """View to archive a conversation."""
    model = Conversation

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.object = self.get_object()
        if request.user not in self.object.users.all():
            raise Http404
        if kwargs['action'] == 'mark-as-unread':
            self.object.unread_by.add(request.user)
        elif kwargs['action'] == 'archive':
            self.object.archived_by.add(request.user)
        if request.is_ajax():
            return HttpResponse('success')
        return HttpResponseRedirect(reverse('conversation_list'))


class BlockTriggerView(RedirectView):
    """View to block/unblock a user."""
    permanent = False

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BlockTriggerView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        # Check if the user exists
        try:
            blocked_user = get_user_model().objects.get(
                pk=kwargs['user_pk'])
        except get_user_model().DoesNotExist:
            return reverse('conversation_list')

        # Block/unblock user
        blocked, created = BlockedUser.objects.get_or_create(
            user=blocked_user, blocked_by=self.request.user)
        if created:
            # Archive all related conversations
            for conversation in self.request.user.conversations.filter(
                    pk__in=blocked_user.conversations.values_list('pk')):
                conversation.archived_by.add(self.request.user)
        else:
            # Unblock user
            blocked.delete()

        # Check for an existing conversation of these users
        conversations = self.request.user.conversations.filter(
            pk__in=blocked_user.conversations.values_list('pk'))
        if conversations:
            return reverse('conversation_update', kwargs={
                'pk': conversations[0].pk})
        return reverse('conversation_list')
