from django.db import models
from django.utils.translation import ugettext_lazy as _


class Story(models.Model):
    url = models.URLField(_('URL'))
    title = models.TextField(_('Title'))
    excerpt = models.TextField(_('Excerpt'), null=True, blank=True)
    created_at = models.TimeField(_('Created at'), auto_now_add=True)
    is_unread = models.BooleanField(_('Is unread?'), default=True)

    class Meta:
        ordering = ['-created_at']
