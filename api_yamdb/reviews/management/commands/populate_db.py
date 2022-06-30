from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

COMMANDS = {
    'populate_users': 'users.csv',
    'populate_genre': 'genre.csv',
    'populate_category': 'category.csv',
    'populate_title': 'titles.csv',
    'populate_genretitle': 'genre_title.csv',
    'populate_review': 'review.csv',
    'populate_comment': 'comments.csv'
}


class Command(BaseCommand):
    help = 'populates db'

    def handle(self, *args, **options):
        for command, csv in COMMANDS.items():
            try:
                call_command(command, csv)
            except Exception as e:
                raise CommandError(
                    f'Cannot run {command} with {csv}. Error: {e}'
                )
        self.stdout.write(self.style.SUCCESS(
            'db is successfully populated with all data needed'
        ))
