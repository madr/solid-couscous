from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods, require_GET

from utsokt.restapi.lib import StoryTeller, JsonApiMapper, StoryMapper
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


def _create_story(post_data):
    url = post_data.get('url', None)
    if not url:
        return HttpResponse(status=400)
    title = post_data.get('title', None)
    excerpt = post_data.get('excerpt', None)
    if not title:
        data = StoryTeller(url)
        title = data.title
        excerpt = data.excerpt
    story, created = Story.objects.get_or_create(url=url)
    story.title = title
    story.excerpt = excerpt
    story.save()
    status = 201 if created else 204
    return HttpResponse(status=status)


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def list_or_create(request):
    if request.method == 'POST':
        return _create_story(request.POST)
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
