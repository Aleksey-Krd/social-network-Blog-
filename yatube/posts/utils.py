from django.core.paginator import Paginator

from .constants import SORT_POSTS_Q


def get_page(posts, request):
    paginator = Paginator(posts, SORT_POSTS_Q)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
