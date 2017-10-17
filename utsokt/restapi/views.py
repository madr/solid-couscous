from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from utsokt.restapi.lib import StoryMapper, create_story
from utsokt.restapi.models import Story


def _list_stories(params):
    filters = {}
    if params.get('read', False):
        filters['is_unread'] = False
    if params.get('unread', False):
        filters['is_unread'] = True
    data = Story.objects.filter(**filters)
    payload = StoryMapper().payload(data)
    return JsonResponse(payload)


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def list_or_create(request):
    if request.method == 'POST':
        return create_story(request.POST)
    elif request.method == 'GET':
        return _list_stories(request.GET)


@csrf_exempt
@require_http_methods(['POST', 'DELETE'])
def modify_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.method == 'DELETE':
        story.delete()
    if request.method == 'POST':
        title = request.POST.get('title', None)
        excerpt = request.POST.get('excerpt', None)
        url = request.POST.get('url', None)
        if url:
            story.url = url
        if title:
            story.title = title
        if excerpt:
            story.excerpt = excerpt
        story.save()
    return HttpResponse(status=204)


@csrf_exempt
@require_POST
def set_story_state(request, story_id, state):
    story = get_object_or_404(Story, id=story_id)
    valid_states = ['read', 'unread']
    if state not in valid_states:
        return HttpResponse(status=400)
    story.is_unread = True if state == 'unread' else False
    story.save()
    return HttpResponse(status=204)
