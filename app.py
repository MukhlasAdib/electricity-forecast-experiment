from src.arg_parser import AppArguments, parse_args
from src.controller import control_data_selection, control_historical_data


def main(args: AppArguments) -> None:
    data = control_data_selection(args.data)
    control_historical_data(data)


if __name__ == "__main__":
    main(parse_args())
