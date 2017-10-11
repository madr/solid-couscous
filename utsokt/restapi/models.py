from django.db import models
from django.utils.translation import ugettext_lazy as _


class Story(models.Model):
    url = models.URLField(_('URL'))
    title = models.CharField(_('Title'), max_length=64)
    excerpt = models.CharField(_('Excerpt'), max_length=64, null=True, blank=True)
    created_at = models.TimeField(_('Created at'), auto_now_add=True)
    is_unread = models.BooleanField(_('Is unread?'), default=True)