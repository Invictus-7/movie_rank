import csv
import os

from django.apps import apps
from django.core.management.base import BaseCommand

from reviews.models import Category, Genre, Review, Title, User


BASE_DICT = {
    'users': ['User', 'reviews', 'filepath'],
    'genre': ['Genre', 'reviews', 'filepath'],
    'titles': ['Title', 'reviews', 'filepath'],
    'comments': ['Comment', 'reviews', 'filepath'],
    'review': ['Review', 'reviews', 'filepath'],
    'category': ['Category', 'reviews', 'filepath'],
    'genre_title': ['Title', 'reviews', 'filepath']
}


class Command(BaseCommand):

    def get_files(self, path):
        """Получение списка файлов для импорта."""
        files = []

        for addresses, dirs, file_names in os.walk(path):
            for file_name in file_names:
                if file_name.endswith('.csv'):
                    file_path = os.path.join(addresses, file_name)
                    files.append(file_path)

        return files

    def transfer(self, base_item):
        """Перенос данных из файла .csv в модель."""
        model_name = BASE_DICT[base_item][0]
        app_name = BASE_DICT[base_item][1]
        file_path = BASE_DICT[base_item][2]

        model = apps.get_model(app_name, model_name)

        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')

            header = next(reader)

            for element in reader:
                object_dict = {key: value for key, value in zip(
                    header, element
                )}

                if model_name == 'Title':
                    category = Category.objects.get(
                        pk=object_dict['category']
                    )
                    object_dict['category'] = category

                if model_name == 'Review':
                    title = Title.objects.get(pk=object_dict['title_id'])
                    object_dict['title'] = title
                    author = User.objects.get(pk=object_dict['author'])
                    object_dict['author'] = author
                    object_dict['score'] = int(object_dict['score'])

                if model_name == 'Comment':
                    author = User.objects.get(pk=object_dict['author'])
                    object_dict['author'] = author
                    review = Review.objects.get(pk=object_dict['review_id'])
                    object_dict['review'] = review

                try:
                    model.objects.create(**object_dict)

                except ValueError:
                    self.stdout.write(
                        self.style.ERROR('Error while transferring data')
                    )

    def through_table_process(self, base_item):
        """Настройка работы промежуточной таблицы GenreTitles."""
        file_path = BASE_DICT[base_item][2]

        with open(file_path, 'r', encoding='utf-8') as csv_file:

            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            header = next(reader)

            for row in reader:
                try:
                    object_dict = {key: value for key, value in zip(
                        header, row
                    )}

                    title = Title.objects.get(pk=object_dict['title_id'])
                    genre, created = Genre.objects.get_or_create(
                        pk=object_dict['genre_id']
                    )

                    if genre and genre not in title.genre.all():
                        title.genre.add(genre)
                        title.save()

                except ValueError:
                    self.stdout.write(
                        self.style.ERROR('Error while creating connection')
                    )

    def handle(self, *args, **options):
        """Исполнение логики работы команды."""
        files = self.get_files(os.getcwd())
        for file_path in files:
            file_name = os.path.basename(file_path).split('.', 1)[0]
            if file_name in BASE_DICT:
                BASE_DICT[file_name][2] = file_path

        self.transfer('users')
        self.transfer('category')
        self.transfer('genre')
        self.transfer('titles')
        self.transfer('review')
        self.transfer('comments')
        self.through_table_process('genre_title')
