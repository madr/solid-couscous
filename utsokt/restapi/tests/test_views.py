import json
from unittest import TestCase
from unittest.mock import patch

from django.test import Client

from utsokt.restapi.lib import StoryTeller
from utsokt.restapi.models import Story


class ModifyStoryTestCase(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        self.story, _ = Story.objects.get_or_create(url='https://example.com', title='Example')

    def test_update_story(self):
        data = {
            'title': 'Another Example',
        }
        response = self.client.post('/api/story/{}'.format(self.story.pk), data=data)
        self.story.refresh_from_db()
        self.assertEqual(self.story.title, data['title'])
        self.assertEqual(response.status_code, 204)

    def test_delete_story(self):
        response = self.client.delete('/api/story/{}'.format(self.story.pk))
        self.assertEqual(Story.objects.filter(id=self.story.pk).count(), 0)
        self.assertEqual(response.status_code, 204)

    def test_not_found(self):
        response = self.client.post('/api/story/{}'.format(self.story.pk + 100), data={})
        self.assertEqual(response.status_code, 404)
        response = self.client.delete('/api/story/{}'.format(self.story.pk + 100), data={})
        self.assertEqual(response.status_code, 404)


class SetStoryStateTestCase(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        self.story, _ = Story.objects.get_or_create(url='https://example.com', title='Example')

    def test_not_found(self):
        response = self.client.post('/api/story/{}'.format(self.story.pk + 100), data={})
        self.assertEqual(response.status_code, 404)
        response = self.client.delete('/api/story/{}'.format(self.story.pk + 100), data={})
        self.assertEqual(response.status_code, 404)

    def test_set_state(self):
        response = self.client.post('/api/story/{}/read'.format(self.story.pk), data={})
        self.story.refresh_from_db()
        self.assertEqual(self.story.is_unread, False)
        self.assertEqual(response.status_code, 204)
        response = self.client.post('/api/story/{}/unread'.format(self.story.pk), data={})
        self.story.refresh_from_db()
        self.assertEqual(self.story.is_unread, True)
        self.assertEqual(response.status_code, 204)


class CreateStoryTestCase(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def test_create_story_successfully(self):
        data = {
            'url': 'https://example.com/hårdrock.html',
            'title': 'Hårdrock!',
            'excerpt': 'Livskvalitet är ekvivalent med hårdrock',
        }
        response = self.client.post('/api/story/', data=data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(Story.objects.get(url='https://example.com/hårdrock.html'))

    def test_silently_updates_story(self):
        data = {
            'url': 'https://example.com/hårdrock.html',
            'title': 'Hårdrock!',
            'excerpt': 'Livskvalitet är ekvivalent med hårdrock'
        }
        self.client.post('/api/story/', data=data)
        data['title'] = 'Hårrock igen!'
        response = self.client.post('/api/story/', data=data)
        self.assertEqual(response.status_code, 204)
        self.assertIsNotNone(Story.objects.get(url='https://example.com/hårdrock.html'))
        self.assertIsNotNone(Story.objects.get(title='Hårrock igen!'))

    def test_create_story_failures(self):
        data = {}
        response = self.client.post('/api/story/', data=data)
        self.assertEqual(response.status_code, 400)

    def test_allow_empty_excerpt(self):
        data = {
            'url': 'https://madr.se',
            'title': 'A title',
        }
        response = self.client.post('/api/story/', data=data)
        self.assertEqual(response.status_code, 201)
        story = Story.objects.get(url='https://madr.se')
        self.assertIsNone(story.excerpt)

    def test_allow_url_only(self):
        data = {
            'url': 'https://madr.se/g',
        }
        mocked_title = 'Hej'
        # should try to get title (and excerpt) from url
        with patch.object(StoryTeller, '_fetch', return_value=(mocked_title, None)) as mock_method:
            response = self.client.post('/api/story/', data=data)
            self.assertEqual(response.status_code, 201)
            mock_method.assert_called_with()
            story = Story.objects.get(url='https://madr.se/g')
            self.assertEqual(story.title, mocked_title)
            self.assertIsNone(story.excerpt)


class ListStoriesTestCase(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        Story.objects.all().delete()
        Story.objects.create(url='http://example.com/1.html', title='Page 1')
        Story.objects.create(url='http://example.com/2.html', title='Page 2', is_unread=False)
        Story.objects.create(url='http://example.com/3.html', title='Page 3', is_unread=False)

    def test_list_stories(self):
        response = self.client.get('/api/story/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        payload = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(payload['data']), 3)
        self.assertEqual(payload['data'][0]['attributes']['title'], 'Page 3')
        self.assertEqual(payload['data'][1]['attributes']['title'], 'Page 2')
        self.assertEqual(payload['data'][2]['attributes']['title'], 'Page 1')

    def test_filter_unread_stories(self):
        response = self.client.get('/api/story/?unread=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        payload = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(payload['data']), 1)
        self.assertEqual(payload['data'][0]['attributes']['title'], 'Page 1')

    def test_filter_read_stories(self):
        response = self.client.get('/api/story/?read=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        payload = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(payload['data']), 2)
        self.assertEqual(payload['data'][0]['attributes']['title'], 'Page 3')
        self.assertEqual(payload['data'][1]['attributes']['title'], 'Page 2')
