import re
from markupsafe import Markup, escape
from app import app
import calendar

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@app.template_filter()
def format_number(number):
    """Converts number to string with space separated thoudands."""
    return 'bez dat' if number is None else ('{:,}'.format(round(number)).replace(',', ' '))


@app.template_filter()
def format_number_delta(number):
    """Converts number to string with space separated thoudands."""
    return 'bez dat' if number is None else (('+' if number > 0 else '') + format_number(number))


@app.template_filter()
def format_decimal(number, digits=1):
    """Converts number to string with space separated thoudands and one digit after decimal point."""
    return 'bez dat' if number is None \
        else ('{:,}'.format(round(number, digits)).replace(',', ' ').replace('.', ','))


@app.template_filter()
def format_decimal_delta(number, digits=1):
    """Converts number to string with space separated thoudands and one digit after decimal point."""
    return 'bez dat' if number is None else (('+' if number > 0 else '') + format_decimal(number, digits))


@app.template_filter()
def format_date(date):
    """Converts date to string in d. m. Y format."""
    return 'bez dat' if date is None else date.strftime('%d. %m. %Y')


@app.template_filter()
def format_date_short(date):
    """Converts date to string in d. m. format."""
    return 'bez dat' if date is None else date.strftime('%d. %m.')


@app.template_filter()
def format_date_wd(date):
    """Converts date to string in a d. m. Y format."""
    return 'bez dat' if date is None else date.strftime('%a %d. %m. %Y').lower()


@app.template_filter()
def format_date_en(date):
    """Converts date to string in Y-m-d format."""
    return 'bez dat' if date is None else date.strftime('%Y-%m-%d')


@app.template_filter()
def format_datetime_short_wd(date):
    """Converts datetime to string in a d. m. H:M format."""
    return 'bez dat' if date is None else date.strftime('%a %d. %m. %H:%M').lower()


@app.template_filter()
def format_weekday(day):
    """Converts number to weekday name."""
    return calendar.day_name[day - 1].capitalize()


@app.template_filter()
def format_time(time):
    """Converts time to string in a H:M format."""
    return 'bez dat' if time is None else time.strftime('%H:%M')


@app.template_filter()
def format_bool(value):
    """Converts boolean to yes/no string."""
    return 'bez dat' if value is None else ('Ano' if value else 'Ne')


@app.template_filter()
def number_color(number, digits=1):
    return '' if number is None or round(number, 1) == 0 else 'text-danger' if round(number, digits) < 0 else 'text-success'


@app.template_filter()
def number_color_rev(number, digits=1):
    return '' if number is None or round(number, 1) == 0 else 'text-danger' if round(number, digits) > 0 else 'text-success'


@app.template_filter()
def nl2br(text):
    return '\n\n'.join(u'%s<br>' % p.replace('\n', Markup('<br>\n')) for p in _paragraph_re.split(escape(text)))
