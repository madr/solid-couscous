from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from urlextract import URLExtract

from utsokt.restapi.lib import create_story


@csrf_exempt
@require_POST
def batch_create(request):
    text = request.POST.get('text', None)
    if not text:
        return HttpResponse(status=400)
    extractor = URLExtract()
    for url in extractor.find_urls(text):
        create_story({'url': url})
    return HttpResponse(status=201)
