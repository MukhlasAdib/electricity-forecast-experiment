from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.constants import DEFAULT_DATA_PATH, DEFAULT_MODEL_PATH


@dataclass
class AppArguments:
    model: Path
    data: Path

    @classmethod
    def from_args_parser(cls, parsed: Any) -> "AppArguments":
        return cls(model=Path(parsed.model), data=Path(parsed.data))


def get_arg_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Tool for monitoring of electricity usage and forecasting",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_PATH,
        help="Path to the Dart LGBM model (.pkl) for minutely forecasting. Defaults to {DEFAULT_MODEL_PATH}",
    )
    parser.add_argument(
        "--data",
        default=DEFAULT_DATA_PATH,
        help=f"Path to the CSV file that contains the electricity usage data. Defaults to {DEFAULT_DATA_PATH}",
    )
    return parser


def parse_args() -> AppArguments:
    return AppArguments.from_args_parser(get_arg_parser().parse_args())
