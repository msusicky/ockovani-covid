from datetime import timedelta

import twitter
from sqlalchemy import text, column

from app import db, app, filters
from app.context import get_import_date
from app.models import CrMetriky


class TwitterBot():
    def __init__(self):
        stats = db.session.query(CrMetriky.ockovani_pocet_plne, CrMetriky.ockovani_pocet_plne_zmena_den,
                                 CrMetriky.ockovani_pocet_3, CrMetriky.ockovani_pocet_3_zmena_den,
                                 CrMetriky.pocet_obyvatel_celkem) \
            .filter(CrMetriky.datum == get_import_date()) \
            .one()

        self._vaccinated_2 = stats.ockovani_pocet_plne
        self._vaccinated_2_diff = stats.ockovani_pocet_plne_zmena_den
        self._vaccinated_2_ratio = stats.ockovani_pocet_plne / stats.pocet_obyvatel_celkem

        self._vaccinated_3 = stats.ockovani_pocet_3
        self._vaccinated_3_diff = stats.ockovani_pocet_3_zmena_den
        self._vaccinated_3_ratio = stats.ockovani_pocet_3 / stats.pocet_obyvatel_celkem

        self.infected_1 = db.session.query(column("nakazeni_celkem_pocet")).from_statement(text(
            """
            select (select sum(pocet) from nakazeni where datum=:datum) + 
                (select pocet from reinfekce where datum=:datum) nakazeni_celkem_pocet
            """
        )).params(datum=get_import_date()-timedelta(1)).one()['nakazeni_celkem_pocet']

        self.infected_8 = db.session.query(column("nakazeni_celkem_pocet")).from_statement(text(
            """
            select (select sum(pocet) from nakazeni where datum=:datum) + 
                (select pocet from reinfekce where datum=:datum) nakazeni_celkem_pocet
            """
        )).params(datum=get_import_date()-timedelta(8)).one()['nakazeni_celkem_pocet']

        infected_diff = self.infected_1 - self.infected_8

        self.infected_sign = 'méně' if infected_diff < 0 else 'více'
        self.infected_diff = abs(infected_diff)

    def post_tweet(self):
        text = self._generate_tweet()
        try:
            self._post_tweet(text)
        except Exception as e:
            app.logger.error(e)
            app.logger.info("Posting tweet '{}' - failed.".format(text))
            return False

        app.logger.info("Posting tweet '{}' - successful.".format(text))
        return True

    def _generate_tweet(self):
        return f"{self._generate_progressbar(self._vaccinated_2_ratio)} 💉💉 ({filters.format_number(self._vaccinated_2)} celkem, {filters.format_number(self._vaccinated_2_diff)} od včera).\n" \
               f"{self._generate_progressbar(self._vaccinated_3_ratio)} 💉💉💉 ({filters.format_number(self._vaccinated_3)} celkem, {filters.format_number(self._vaccinated_3_diff)} od včera).\n" \
               f"Včera přibylo {filters.format_number(self.infected_1)} nakažených, o {filters.format_number(self.infected_diff)} {self.infected_sign} než před týdnem. " \
               f"https://ockovani.opendatalab.cz"

    def _generate_progressbar(self, ratio):
        vaccinated_percent = ratio * 100
        vaccinated_progress = ratio * 20

        progressbar = ''

        for i in range(1, 21):
            if i <= vaccinated_progress:
                progressbar += '▓'
            else:
                progressbar += '░'

        return progressbar + ' ' + filters.format_decimal(vaccinated_percent, 1) + ' %'

    def _days(self, days):
        if days is None:
            days = 0

        if days == 1:
            return filters.format_number(days) + " den"
        elif days >= 2 and days <= 4:
            return filters.format_number(days) + " dny"
        else:
            return filters.format_number(days) + " dní"

    def _post_tweet(self, text):
        api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                          consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                          access_token_key=app.config['TWITTER_ACCESS_TOKEN_KEY'],
                          access_token_secret=app.config['TWITTER_ACCESS_TOKEN_SECRET'])
        api.PostUpdate(text)


if __name__ == '__main__':
    twitter_bot = TwitterBot()
    print(twitter_bot._generate_tweet())
