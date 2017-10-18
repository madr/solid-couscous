from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from utsokt.batch_create.lib import extract_and_create_stories


@csrf_exempt
@require_POST
def batch_create(request):
    text = request.POST.get('text', None)
    if not text:
        return HttpResponse(status=400)
    extract_and_create_stories(text)
    return HttpResponse(status=201)
