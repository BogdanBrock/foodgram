"""Пагинация для API."""

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пагинатор CustomPagination."""

    page_size = 6
    page_size_query_param = 'limit'
