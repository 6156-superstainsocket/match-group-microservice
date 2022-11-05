from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 10 # default page size
    page_size_query_param = 'size' # page size query parameter
    max_page_size = 100 # max page size