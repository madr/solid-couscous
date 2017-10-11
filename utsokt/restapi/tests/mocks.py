PAGE_TITLE = 'Sidtitel'
OG_TITLE = 'OGTitel'
OG_DESCRIPTION = 'Blåbärsöl'
URL_NO_OG = 'http://example.com/no-og.html'
URL_NO_OG_TITLE = 'http://example.com/no-og-title.html'
URL_FULL_OG = 'http://example.com/og.html'
URL_NO_TITLE = 'http://example.com/empty.html'


def mocked_requests_get(*args, **kwargs):
    html_og = '<html><head><title>{}</title><meta property="og:title" content="{}"><meta property="og:description" content="{}"></head></html>'.format(
        PAGE_TITLE, OG_TITLE, OG_DESCRIPTION)
    html_og_no_title = '<html><head><title>{}</title><meta property="og:description" content="{}"></head></html>'.format(
        PAGE_TITLE, OG_DESCRIPTION)
    html_no_og = '<html><head><title>{}</title></head></html>'.format(PAGE_TITLE)
    html_empty = '<html></html>'

    class MockResponse:
        def __init__(self, html_data, status_code):
            self.text = html_data
            self.status_code = status_code

    if args[0] == URL_FULL_OG:
        return MockResponse(html_og, 200)
    elif args[0] == URL_NO_OG:
        return MockResponse(html_no_og, 200)
    elif args[0] == URL_NO_OG_TITLE:
        return MockResponse(html_og_no_title, 200)
    elif args[0] == URL_NO_TITLE:
        return MockResponse(html_empty, 200)
    return MockResponse(None, 404)
