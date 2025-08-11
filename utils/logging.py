"""Lightweight logging utilities with optional Rich formatting.

Falls back to plain prints if Rich is unavailable.
"""

from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

_console = Console()


def log_info(message: str) -> None:
    if _console:
        _console.log(message)
    else:
        print(message)


def log_error(message: str) -> None:
    if _console:
        _console.log(f"[red]{message}[/red]")
    else:
        print(message)


def log_markdown(md_text: str) -> None:
    if _console:
        _console.print(Markdown(md_text))
    else:
        print(md_text)


def log_panel(title: str, content: str) -> None:
    if _console:
        _console.print(Panel.fit(content, title=title))
    else:
        print(f"--- {title} ---\n{content}")


def log_dataframe(df: Any, title: str | None = None) -> None:
    if _console:
        try:
            table = Table(title=title)
            for col in df.columns:
                table.add_column(str(col))
            for _, row in df.iterrows():
                table.add_row(*[str(v) for v in row.tolist()])
            _console.print(table)
            return
        except Exception as err:
            _console.log(
                f"[yellow]Fallback to plain dataframe render due to error:[/yellow] {err}"
            )
    # Fallback
    if title:
        print(f"--- {title} ---")
    try:
        print(df.to_string(index=False))
    except Exception:
        print(str(df))


def log_markdown_panel(title: str, md_text: str) -> None:
    """Render markdown content inside a titled panel.

    Falls back to plain text if Rich is unavailable.
    """
    if _console:
        _console.print(Panel.fit(Markdown(md_text), title=title))
    else:
        print(f"--- {title} ---\n{md_text}")
