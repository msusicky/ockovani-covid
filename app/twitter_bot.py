from datetime import timedelta

import twitter

from app import db, app, filters, queries
from app.context import get_import_date
from app.models import CrMetriky


class TwitterBot():
    def __init__(self):
        stats = db.session.query(CrMetriky.ockovani_pocet_plne, CrMetriky.ockovani_pocet_plne_zmena_den,
                                 CrMetriky.pocet_obyvatel_celkem, CrMetriky.registrace_pred_zavorou,
                                 CrMetriky.registrace_median_cekani) \
            .filter(CrMetriky.datum == get_import_date()) \
            .one()

        self._vaccinated = stats.ockovani_pocet_plne
        self._vaccinated_diff = stats.ockovani_pocet_plne_zmena_den
        self._vaccinated_ratio = (1.0 * stats.ockovani_pocet_plne) / stats.pocet_obyvatel_celkem
        self._waiting = stats.registrace_pred_zavorou
        self._average_reservation_waiting = stats.registrace_median_cekani
        # self._end_date = queries.count_end_date_vaccinated()
        # self._end_date_supplies = queries.count_end_date_supplies()
        # self._end_date_interested = queries.couht_end_date_interested()
        # self._interest_all = queries.count_interest()[0]
        self._gp_vaccines = queries.couht_gp_vaccines()

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
        return f"{self._generate_progressbar()} plně očkováno ({filters.format_number(self._vaccinated)} celkem, {filters.format_number(self._vaccinated_diff)} od včera). " \
               f"Na termín pro 1. nebo 3. dávku čeká před závorou {filters.format_number(self._waiting)} zájemců, průměrná doba čekání je {filters.format_number(self._average_reservation_waiting)} dní. " \
               f"Praktici nabízejí {filters.format_number(self._gp_vaccines)} dávek. https://ockovani.opendatalab.cz"

    def _generate_progressbar(self):
        vaccinated_percent = self._vaccinated_ratio * 100
        vaccinated_progress = self._vaccinated_ratio * 20

        progressbar = ''

        for i in range(1, 21):
            if i <= vaccinated_progress:
                progressbar += '▓'
            else:
                progressbar += '░'

        return progressbar + ' ' + filters.format_decimal(vaccinated_percent, 1) + ' %'

    def _post_tweet(self, text):
        api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                          consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                          access_token_key=app.config['TWITTER_ACCESS_TOKEN_KEY'],
                          access_token_secret=app.config['TWITTER_ACCESS_TOKEN_SECRET'])
        api.PostUpdate(text)


if __name__ == '__main__':
    twitter_bot = TwitterBot()
    print(twitter_bot._generate_tweet())
