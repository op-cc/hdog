from django.http import HttpResponse


def stock_overview(request):
    html = "<html><body>Hello, world!</body></html>"
    return HttpResponse(html)
