from datetime import date, timedelta

import twitter
from sqlalchemy import func

from app import db, app, filters, queries
from app.models import KrajMetriky


class TwitterBot():
    def __init__(self):
        stats = db.session.query(func.sum(KrajMetriky.ockovani_pocet_2).label('ockovani_plne'),
                                 func.sum(KrajMetriky.ockovani_pocet_2_zmena_den).label('ockovani_plne_zmena_den'),
                                 func.sum(KrajMetriky.pocet_obyvatel_dospeli).label('pocet_obyvatel'),
                                 func.sum(KrajMetriky.ockovani_pocet).label("ockovane_davky_celkem"),
                                 func.sum(KrajMetriky.ockovani_pocet_zmena_tyden).label("ockovane_davky_tyden"),
                                 func.sum(KrajMetriky.registrace_fronta).label('fronta')) \
            .filter(KrajMetriky.datum == queries.last_import_date()) \
            .one_or_none()

        remaining_days = (7 * (2 * 0.7 * stats.pocet_obyvatel - stats.ockovane_davky_celkem)) / stats.ockovane_davky_tyden

        self._vaccinated = stats.ockovani_plne
        self._vaccinated_diff = stats.ockovani_plne_zmena_den
        self._vaccinated_ratio = (1.0 * stats.ockovani_plne) / stats.pocet_obyvatel
        self._population = stats.pocet_obyvatel
        self._waiting = stats.fronta
        self._end_date = date.today() + timedelta(remaining_days)

    def post_tweet(self):
        text = self._generate_tweet()
        self._post_tweet(text)

    def _generate_tweet(self):
        text = "{} plně očkováno ({} celkem, {} včera). Na přidělení termínu aktuálně čeká {} zájemců. Aktuální rychlostí bude 70 % dospělé populace naočkováno přibližně {}. #COVID19 https://ockovani.opendatalab.cz" \
            .format(self._generate_progressbar(), filters.format_number(self._vaccinated),
                    filters.format_number(self._vaccinated_diff), filters.format_number(self._waiting),
                    filters.format_date(self._end_date))
        return text

    def _generate_progressbar(self):
        vaccinated_percent = self._vaccinated_ratio * 100
        vaccinated_progress = self._vaccinated_ratio * 20

        progressbar = ''

        for i in range(1, 21):
            if i <= vaccinated_progress:
                progressbar += '▓'
            else:
                progressbar += '░'

        return progressbar + ' ' + filters.format_decimal(vaccinated_percent, 2) + ' %'

    def _post_tweet(self, text):
        api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                          consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                          access_token_key=app.config['TWITTER_ACCESS_TOKEN_KEY'],
                          access_token_secret=app.config['TWITTER_ACCESS_TOKEN_SECRET'])
        api.PostUpdate(text)


if __name__ == '__main__':
    twitter_bot = TwitterBot()
    print(twitter_bot._generate_tweet())
