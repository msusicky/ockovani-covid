from app import app


@app.template_filter()
def format_number(number):
    """Converts number to string with space separated thoudands."""
    return '{:,}'.format(number).replace(',', ' ')


@app.template_filter()
def format_decimal(number):
    """Converts number to string with space separated thoudands and one digit after decimal point."""
    return 'bez dat' if number is None else '{:,}'.format(round(number, 1)).replace(',', ' ').replace('.', ',')


@app.template_filter()
def format_date(date):
    """Converts date to string in d. m. Y format."""
    return date.strftime('%d. %m. %Y').lower()


@app.template_filter()
def format_date_wd(date):
    """Converts date to string in a d. m. Y format."""
    return date.strftime('%a %d. %m. %Y').lower()


@app.template_filter()
def format_datetime_short_wd(date):
    """Converts datetime to string in a d. m. H:M format."""
    return date.strftime('%a %d. %m. %H:%M').lower()
