from rich.console import Console
from rich.table import Table
from rich.panel import Panel


from ota.core.models import Columns

console = Console()

COLUMNS = Columns(
    integer={"justify": "center", "style": "green"},
    name={"style": "magenta", "no_wrap": True},
)

# DEFAULT_OPTIONS = {
#     "name": {"style": "magenta", "no_wrap": True},
# }
