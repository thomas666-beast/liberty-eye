from django import template

register = template.Library()

@register.filter
def first_record(history, record_type):
    """Return the first record of a specific type from history"""
    for record in history:
        if record.record_type == record_type:
            return record
    return None

@register.filter
def record_color(record_type):
    """Return a color based on record type"""
    color_map = {
        'activity': 'primary',
        'activity_address': 'info',
        'job': 'success',
        'job_address': 'warning',
        'address': 'purple'
    }
    return color_map.get(record_type, 'secondary')

@register.filter
def record_icon(record_type):
    """Return an icon based on record type"""
    icon_map = {
        'activity': 'fa-running',
        'activity_address': 'fa-map-marker-alt',
        'job': 'fa-briefcase',
        'job_address': 'fa-building',
        'address': 'fa-home'
    }
    return icon_map.get(record_type, 'fa-history')
