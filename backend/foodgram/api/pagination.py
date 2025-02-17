from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

    def get_paginated_response_schema(self, schema):
        return super().get_paginated_response_schema(schema)

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return int(request.query_params[self.page_size_query_param])
            except (KeyError, ValueError):
                pass
        return self.page_size

    def get_next_link(self):
        if self.page.has_next():
            url = self.request.build_absolute_uri()
            return f'{url}?page={self.page.next_page_number()}'

    def get_previous_link(self):
        if self.page.has_previous():
            url = self.request.build_absolute_uri()
            return f'{url}?page={self.page.previous_page_number()}'


class CustomUserlistPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        }
