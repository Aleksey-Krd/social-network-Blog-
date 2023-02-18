from django.shortcuts import render, render_to_response


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    return render_to_response('core/403csrf.html')


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)
