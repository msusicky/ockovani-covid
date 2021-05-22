import time
from datetime import date, timedelta

import click

from app import app
from app.etl import MetricsEtl
from app.fetcher import FetcherLauncher
from app.twitter_bot import TwitterBot
from app.verifier import Verifier


@app.cli.command('fetch-data')
@click.argument('dataset')
def fetch_data_command(dataset):
    """Fetch opendata from UZIS."""
    start = time.time()
    app.logger.info("Fetching data started.")
    fetcher = FetcherLauncher()
    result = fetcher.fetch(dataset)

    if result:
        app.logger.info("Fetching data finished successfully in {:.1f} s.".format(time.time() - start))
        exit(0)
    else:
        app.logger.error("Fetching data failed.")
        exit(1)


@app.cli.command('compute-metrics')
@click.argument("metric")
@click.argument("datum", nargs=-1)
def compute_metrics_command(metric, datum):
    """Compute metrics."""
    start = time.time()
    app.logger.info("Computing metrics started.")

    if len(datum) == 2:
        start_date = date.fromisoformat(datum[0])
        end_date = date.fromisoformat(datum[1])
    elif len(datum) == 1:
        start_date = date.fromisoformat(datum[0])
        end_date = date.fromisoformat(datum[0])
    else:
        start_date = date.today()
        end_date = date.today()

    result = True

    while start_date <= end_date:
        app.logger.info("Computing metrics for date: '{}'.".format(start_date))
        etl = MetricsEtl(start_date)
        result = etl.compute(metric)
        if not result:
            break
        start_date += timedelta(1)

    if result:
        app.logger.info("Computing metrics finished successfully in {:.1f} s.".format(time.time() - start))
        exit(0)
    else:
        app.logger.error("Computing metrics failed.")
        exit(1)


@app.cli.command('verify-data')
def verify_data_command():
    """Verify if data are not same as yesterday."""
    result = Verifier.verify_data()

    if result:
        exit(0)
    else:
        exit(1)


@app.cli.command('post-tweet')
def post_tweet_command():
    """Post statistics as a tweet."""
    twitter_bot = TwitterBot()
    result = twitter_bot.post_tweet()

    if result:
        exit(0)
    else:
        exit(1)
