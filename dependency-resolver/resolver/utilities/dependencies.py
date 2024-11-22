import logging
from sys import executable
from . import run

_logger = logging.getLogger(__name__)

def installPackages(packages:list[str]) :
    for package in packages :
        try:
            if len(packages) > 0:
                parameters:list[any] = [executable, "-m", "pip", "install", package]
                run.runExternalArgs(parameters, False)
                print(f"Installed package: {package}")
                _logger.info(f"Installed package: {package}")

        except Exception as e:
            print(f"Failed to install package {package}")
            _logger.error(f"Failed to install package {package} :", e)