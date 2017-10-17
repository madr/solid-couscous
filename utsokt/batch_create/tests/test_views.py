from unittest import TestCase
from unittest.mock import patch

from django.test import Client

from utsokt.restapi.lib import StoryTeller
from utsokt.restapi.models import Story


class BatchCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        Story.objects.all().delete()

    def test_does_nothing_without_text(self):
        response = response = self.client.post('/batch/', data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Story.objects.all().count(), 0)

    def test_create_stories_from_text(self):
        text = 'https://example.com/1/ ' \
               'https://example.com/2'
        data = {
            'text': text
        }
        mocked_title = 'Hej'
        with patch.object(StoryTeller, '_fetch', return_value=(mocked_title, None)) as mock_method:
            response = self.client.post('/batch/', data=data)
            self.assertEqual(response.status_code, 201)
            mock_method.assert_called_with()
            stories = Story.objects.all()
            self.assertEqual(stories.count(), 2)
            self.assertEqual(stories.filter(url='https://example.com/1/').count(), 1)
            self.assertEqual(stories.filter(url='https://example.com/2').count(), 1)

    def test_handles_urls_from_html(self):
        text = 'https://example.com/0/ ' \
               '<p>https://example.com/1/</p>, ' \
               '<a href="https://example.com/2">Test</a>'
        data = {
            'text': text
        }
        mocked_title = 'Hej'
        with patch.object(StoryTeller, '_fetch', return_value=(mocked_title, None)) as mock_method:
            response = self.client.post('/batch/', data=data)
            self.assertEqual(response.status_code, 201)
            mock_method.assert_called_with()
            stories = Story.objects.all()
            self.assertEqual(stories.count(), 3)
            self.assertEqual(stories.filter(url='https://example.com/0/').count(), 1)
            self.assertEqual(stories.filter(url='https://example.com/1/').count(), 1)
            self.assertEqual(stories.filter(url='https://example.com/2').count(), 1)
