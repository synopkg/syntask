"""
Utilities for Syntask CLI commands
"""

import functools
import traceback
from typing import NoReturn

import typer
from click.exceptions import ClickException

from syntask.exceptions import MissingProfileError
from syntask.settings import SYNTASK_TEST_MODE


def exit_with_error(message, code=1, **kwargs) -> NoReturn:
    """
    Utility to print a stylized error message and exit with a non-zero code
    """
    from syntask.cli.root import app

    kwargs.setdefault("style", "red")
    app.console.print(message, **kwargs)
    raise typer.Exit(code)


def exit_with_success(message, **kwargs) -> NoReturn:
    """
    Utility to print a stylized success message and exit with a zero code
    """
    from syntask.cli.root import app

    kwargs.setdefault("style", "green")
    app.console.print(message, **kwargs)
    raise typer.Exit(0)


def with_cli_exception_handling(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (typer.Exit, typer.Abort, ClickException):
            raise  # Do not capture click or typer exceptions
        except MissingProfileError as exc:
            exit_with_error(exc)
        except Exception:
            if SYNTASK_TEST_MODE.value():
                raise  # Reraise exceptions during test mode
            traceback.print_exc()
            exit_with_error("An exception occurred.")

    return wrapper
