from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    # the number of items returned per page)
    page_size = 10
    # Defines the name for the query parameter to use for the page size
    page_size_query_param = 'page_size'
    # Indicates the maximum requested page size allowed
    max_page_size = 50
