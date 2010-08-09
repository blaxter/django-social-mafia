import urlparse
from django.core.management.base import BaseCommand

from social_mafia.models import User, Story, Vote

import meneame
class Command(BaseCommand):
    args = '<limit>'
    help = 'Imports <limit> articles from meneame'

    def handle(self, *args, **options):
        if not len(args):
            print self.help
            return

        limit = int(args[0])
        for url in meneame.get_articles(limit):
            slug = url.split('/')[2]
            story, _ = Story.objects.get_or_create(slug=slug)
            url = urlparse.urljoin('http://www.meneame.net', url)
            stats = meneame.get_article_stats(url)
            for vote in stats['votes']:
                user, _ = User.objects.get_or_create(name=vote['user'])
                v = Vote(user=user, story=story, value=vote['value'])
                v.save()
