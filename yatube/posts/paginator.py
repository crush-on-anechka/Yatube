from django.core.paginator import Paginator

LIMIT_POSTS: int = 10


def paginator(request, posts):
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
