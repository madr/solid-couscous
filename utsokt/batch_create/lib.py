from urlextract import URLExtract

from utsokt.restapi.lib import create_story


def extract_and_create_stories(text):
    extractor = URLExtract()
    for url in extractor.find_urls(text):
        create_story({'url': url})
