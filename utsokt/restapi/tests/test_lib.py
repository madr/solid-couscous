from unittest.mock import patch

from django.test import TestCase

from utsokt.restapi.lib import StoryTeller
from utsokt.restapi.tests.mocks import (
    mocked_requests_get, PAGE_TITLE, OG_TITLE, OG_DESCRIPTION, URL_NO_OG_TITLE,
    URL_FULL_OG,
    URL_NO_OG, URL_NO_TITLE)


class StoryTellerTestCase(TestCase):
    @patch('requests.get', side_effect=mocked_requests_get)
    def test_captures_meta_data(self, *args):
        story = StoryTeller(URL_NO_OG_TITLE)
        self.assertEqual(story.title, PAGE_TITLE)
        self.assertEqual(story.excerpt, OG_DESCRIPTION)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_og_title_overrides_title(self, *args):
        story = StoryTeller(URL_FULL_OG)
        self.assertEqual(story.title, OG_TITLE)
        self.assertEqual(story.excerpt, OG_DESCRIPTION)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_og_not_found(self, *args):
        story = StoryTeller(URL_NO_OG)
        self.assertEqual(story.title, PAGE_TITLE)
        self.assertEqual(story.excerpt, None)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_title_fallback(self, *args):
        story = StoryTeller(URL_NO_TITLE)
        self.assertEqual(story.title, URL_NO_TITLE)
        self.assertEqual(story.excerpt, None)