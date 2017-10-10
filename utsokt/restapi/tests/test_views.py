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
