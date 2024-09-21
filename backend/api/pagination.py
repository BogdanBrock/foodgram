"""Пагинация для API."""

from rest_framework.pagination import PageNumberPagination

from . import constants


class CustomPagination(PageNumberPagination):
    """Пагинатор CustomPagination."""

    page_size = constants.PAGE_SIZE
    page_size_query_param = 'limit'
