import re

import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse

from utsokt.restapi.models import Story


class StoryTeller:
    def __init__(self, url):
        self.url = url
        self.title, self.excerpt = self._fetch()

    def _fetch(self):
        title = None
        excerpt = None
        response = requests.get(self.url)
        doc = BeautifulSoup(response.text, 'html.parser')
        if doc.title:
            title = doc.title.string
        for og_data in doc.find_all('meta', attrs={'property': re.compile(r'^og\:')}):
            if og_data.attrs['property'] == 'og:title':
                title = og_data.attrs['content']
            if og_data.attrs['property'] == 'og:description':
                excerpt = og_data.attrs['content']
        if not title:
            title = self.url
        return title, excerpt


class JsonApiMapper:
    def attributes(self, item):
        raise NotImplemented

    def payload(self, data):
        return {
            'data': [{
                'type': 'story',
                'id': item.id,
                'attributes': self.attributes(item)
            } for item in data],
            'version': '1.0',
        }


class StoryMapper(JsonApiMapper):
    def attributes(self, item):
        return {
            'url': item.url,
            'title': item.title,
            'excerpt': item.excerpt,
        }


def create_story(input_data):
    url = input_data.get('url', None)
    if not url:
        return HttpResponse(status=400)
    title = input_data.get('title', None)
    excerpt = input_data.get('excerpt', None)
    if not title:
        story_data = StoryTeller(url)
        title = story_data.title
        excerpt = story_data.excerpt
    story, created = Story.objects.get_or_create(url=url)
    story.title = title
    story.excerpt = excerpt
    story.save()
    status = 201 if created else 204
    return HttpResponse(status=status)