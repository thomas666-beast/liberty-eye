from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    """
    Builds a query string that preserves existing GET parameters while updating specified ones.
    Usage: {% query_string page=2 %}
    """
    request = context['request']
    query_dict = request.GET.copy()

    for key, value in kwargs.items():
        if value is None:
            if key in query_dict:
                del query_dict[key]
        else:
            query_dict[key] = value

    return urlencode(query_dict)
