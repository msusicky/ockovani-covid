from app import app
from app.opendata_fetcher import OpendataFetcher


@app.cli.command('fetch-reservatic')
def fetch_reservatic_command():
    """Fetch free capacities from Reservatic."""
    pass

@app.cli.command('fetch-opendata')
def fetch_opendata_command():
    """Fetch opendata from UZIS."""
    fetcher = OpendataFetcher()
    fetcher.fetch_all()