from rich.console import Console
from rich.table import Table
from rich.panel import Panel


from ota.core.models import Columns

console = Console()

COLUMNS = Columns(
    integer={"justify": "center", "style": "green"},
    primary_integer={"justify": "center", "style": "red"},
    name={"style": "magenta", "no_wrap": True},
    text_left={"justify": "left", "style": "cyan", "no_wrap": False},
    text_right={"justify": "right", "style": "cyan", "no_wrap": False},
    text_center={"justify": "center", "no_wrap": True},
)
