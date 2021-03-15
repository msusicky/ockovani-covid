import twitter

from app import db, app
from app.models import KrajMetriky


class TwitterBot():
    def __init__(self):
        # stats = db.session.query(KrajMetriky.ockovani_pocet_2, KrajMetriky.ockovani_pocet_2_zmena_den,
        #                          KrajMetriky.pocet_obyvatel_dospeli) \
        #     .one_or_none()

        pass


    def _generate_tweet(self):
        return self._generate_progressbar(0.99)


    def _generate_progressbar(self, vaccinated):
        res = vaccinated * 20

        progress = ''

        for i in range(1, 21):
            if i <= res:
                progress += '▓'
            else:
                progress += '░'

        progress += ' ' + str(100 * vaccinated) + '%'

        return progress


    def _send_tweet(self):
        api = twitter.Api(consumer_key=app.config['TWITTER_CONSUMER_KEY'],
                          consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
                          access_token_key=app.config['TWITTER_ACCESS_TOKEN_KEY'],
                          access_token_secret=app.config['TWITTER_ACCESS_TOKEN_SECRET'])

        api.PostUpdate('Test!')


if __name__ == '__main__':
    twitter_bot = TwitterBot()
    print(twitter_bot._generate_tweet())