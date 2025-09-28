import argparse
import logging
import sys

from interfaces.gradio_ui import AutoDevSuiteUI
from utils.logger_setup import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Точка входа в приложение"""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="AutoDevSiute", usage="python app.py [команда] [опции]"
    )

    parser.add_argument(
        "--ui", action="store_true", help="Запуск вэб интерфейса Gradio"
    )
    parser.add_argument("--port", action="store_true", default=7860)

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.ui:
        ui = AutoDevSuiteUI()
        ui.run()


if __name__ == "__main__":
    main()
