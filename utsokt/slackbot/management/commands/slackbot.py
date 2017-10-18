from utsokt.batch_create.lib import extract_and_create_stories
from utsokt.slackbot.models import Team
from slackclient import SlackClient
from django.core.management.base import BaseCommand
import time


class Command(BaseCommand):
    help = 'Starts the slack bot'

    def start_listening(self):
        team = Team.objects.first()
        client = SlackClient(team.bot_access_token)
        if client.rtm_connect():
            while True:
                events = client.rtm_read()
                for event in events:
                    if 'text' in event and 'type' in event and event['type'] == 'message':
                        extract_and_create_stories(event['text'])
                        client.rtm_send_message(
                            event['channel'],
                            'Thank you!'
                        )
                time.sleep(1)

    def handle(self, *args, **options):
        self.start_listening()
