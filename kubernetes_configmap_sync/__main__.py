import logging
import sys

from .app import execute_configmap_sync

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def _print_help():
    """ Prints the help to use the script. """
    LOGGER.info('The script should be run with the following parameters:')
    LOGGER.info('python3 -m kubernetes_configmap_sync <configmap_directory>')
    LOGGER.info('- configmap_directory: the root directory where config map data are stored.')


if __name__ == '__main__':
    # Files found.
    if len(sys.argv) != 2:
        LOGGER.error("ConfigMap directory must be defined")
        _print_help()
        sys.exit(1)

    execute_configmap_sync(sys.argv[1])
