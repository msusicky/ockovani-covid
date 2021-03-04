from app import app


@app.template_filter()
def format_number(number):
    """Converts number to string with space separated thoudands."""
    return '{:,}'.format(number).replace(',', ' ')

@app.template_filter()
def format_date(date):
    """Converts date to string in d. m. Y format."""
    return date.strftime('%d. %m. %Y')