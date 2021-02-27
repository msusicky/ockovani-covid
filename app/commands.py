from app import app
from app.opendata_fetcher import OpendataFetcher
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
    fetcher = OpendataFetcher()
    fetcher.fetch_all()

@app.cli.command('fetch-sheet')
def fetch_sheet_command():
    """Fetch sheet from Google Sheets."""
    fetcher = SheetFetcher()
    fetcher.fetch_centers()