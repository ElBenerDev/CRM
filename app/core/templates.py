from fastapi.templating import Jinja2Templates
from datetime import datetime
from .config import settings

def format_date(date):
    if date is None:
        return datetime.utcnow().strftime('%d/%m/%Y')
    return date.strftime('%d/%m/%Y')

templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)
templates.env.filters["format_date"] = format_date