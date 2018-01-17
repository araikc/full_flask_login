# This will be used in JINJA2 for filtering data from {{ }}

from .. import application

@application.template_filter('make_caps')
def caps(text):
    """Convert a string to all caps."""
    return text.uppercase()
