"""Файл для загрузки ингредиентов в БД."""

import os
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Класс для создания ингредиентов в БД."""

    def add_arguments(self, parser):
        """Функция для добавления передачи пути к JSON файлу."""
        parser.add_argument('ingredients.json', type=str)

    def handle(self, *args, **options):
        """Функция для создания ингредиентов в БД."""
        json_file = options['ingredients.json']
        file_path = os.path.join(settings.BASE_DIR, '..', 'data', json_file)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for item in data:
                Ingredient.objects.create(**item)

            self.stdout.write(self.style.SUCCESS(
                'Данные успешно были загружены'
            )
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(
                'Ошибка декодирования JSON файла, '
                'пожалуйста, проверьте формат файла'
            )
            )
