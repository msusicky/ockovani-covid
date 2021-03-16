import time
from datetime import date, timedelta

import click

from app import app
from app.etl import Etl
from app.opendata_fetcher import OpenDataFetcher
from app.twitter_bot import TwitterBot


@app.cli.command('fetch-opendata')
def fetch_opendata_command():
    """Fetch opendata from UZIS."""
    start = time.time()
    app.logger.info("Fetching opendata started.")
    fetcher = OpenDataFetcher()
    result = fetcher.fetch_all()
    if result:
        end = time.time()
        app.logger.info("Fetching opendata finished successfully in {:.1f} s.".format(end - start))
        exit(0)
    else:
        app.logger.error("Fetching opendata failed.")
        exit(1)


@app.cli.command('compute-metrics')
@click.argument("datum", nargs=-1)
def compute_metrics_command(datum):
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
        etl = Etl(start_date)
        result = etl.compute_all()
        if not result:
            break
        start_date += timedelta(1)

    if result:
        end = time.time()
        app.logger.info("Computing metrics finished successfully in {:.1f} s.".format(end - start))
        exit(0)
    else:
        app.logger.error("Computing metrics failed.")
        exit(1)


@app.cli.command('post-tweet')
def post_tweet_command():
    """Post statistics as a tweet."""
    twitter_bot = TwitterBot()
    twitter_bot.post_tweet()
