from rich.console import Console
from rich.table import Table
from rich.panel import Panel


from ota.core.models import Columns

console = Console()

COLUMNS = Columns(
    integer={"justify": "center", "style": "green"},
    primary_integer={"justify": "center", "style": "red"},
    name={"style": "magenta", "no_wrap": True},
    text_right={"justify": "right", "style": "blue", "no_wrap": False},
)

# DEFAULT_OPTIONS = {
#     "name": {"style": "magenta", "no_wrap": True},
# }
