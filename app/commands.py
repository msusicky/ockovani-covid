from app import app
from app.opendata_fetcher import OpenDataFetcher
from app.reservatic_fetcher import ReservaticFetcher
from app.sheet_fetcher import SheetFetcher


@app.cli.command('fetch-reservatic')
def fetch_reservatic_command():
    """Fetch free capacities from Reservatic."""
    fetcher = ReservaticFetcher()
    fetcher.fetch_free_capacities()

@app.cli.command('fetch-opendata')
def fetch_opendata_command():
    """Fetch opendata from UZIS."""
    app.logger.info("Fetching opendata started.")
    fetcher = OpenDataFetcher()
    result = fetcher.fetch_all()
    if result:
        app.logger.info("Fetching opendata was successful.")
        exit(0)
    else:
        app.logger.error("Fetching opendata failed.")
        exit(1)

@app.cli.command('fetch-sheet')
def fetch_sheet_command():
    """Fetch sheet from Google Sheets."""
    fetcher = SheetFetcher()
    fetcher.fetch_centers()

@app.cli.command('fetch-all')
def fetch_all_command():
    """Execute all fetchers."""
    opendata_fetcher = OpenDataFetcher()
    opendata_fetcher.fetch_all()

    sheet_fetcher = SheetFetcher()
    sheet_fetcher.fetch_centers()

    reservatic_fetcher = ReservaticFetcher()
    reservatic_fetcher.fetch_free_capacities()