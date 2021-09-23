import argparse
import logging
import os
import sys
from pprint import pformat
from bridge.deploy.registry import DEPLOY_REGISTRY
from bridge.analytics import AnalyticsClient

# The minimal required version of Python
MIN_PYTHON_VERSION = (3,9)

def cli_init(args):
    logger = logging.getLogger(__name__)
    deploy_client = DEPLOY_REGISTRY[args.deploy_service]()
    logger.info(f"Initializing Bridge '{pformat(args)}'.")
    deploy_client.init()
    AnalyticsClient(deploy_client).track_deploy_client_init()


def cli_destroy(args):
    logger = logging.getLogger(__name__)
    deploy_client = DEPLOY_REGISTRY[args.deploy_service]()
    logger.info(f"Destroying Bridge '{pformat(args)}'.")
    deploy_client.teardown()
    AnalyticsClient(deploy_client).track_deploy_client_destroy()


def cli_run(args):
    from bridge.app import main

    logger = logging.getLogger(__name__)
    logger.info(f"Starting Bridge '{pformat(args)}'.")
    main()


def main():
    if sys.version_info < MIN_PYTHON_VERSION:
        raise AssertionError("Invalid Python version")

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    level = logging.getLevelName(LOG_LEVEL)
    logging.basicConfig(level=level)

    logger = logging.getLogger(__name__)

    # Main Parser
    main_parser = argparse.ArgumentParser(
        prog="bridge",
        description=(
            "Tool to sync model registries with" " production deployments."
        ),
    )
    subparsers = main_parser.add_subparsers()

    # Init
    init_parser = subparsers.add_parser(
        "init", help="Create global cloud resources needed for deployment."
    )
    init_parser.add_argument(
        "deploy_service",
        choices=list(DEPLOY_REGISTRY.keys()),
        help="The model deployment provider.",
    )
    init_parser.set_defaults(func=cli_init)

    # Destroy
    destroy_parser = subparsers.add_parser(
        "destroy",
        help=(
            "Delete all deployments and global cloud resources "
            "created by 'init'."
        ),
    )
    destroy_parser.add_argument(
        "deploy_service",
        choices=list(DEPLOY_REGISTRY.keys()),
        help="The model deployment provider.",
    )
    destroy_parser.set_defaults(func=cli_destroy)

    # Run
    run_parser = subparsers.add_parser(
        "run",
        help="Start watcher service to automatically manage deployments.",
    )
    run_parser.set_defaults(func=cli_run)

    args, config = main_parser.parse_known_args()
    args.config = config
    logger.debug(args)

    if hasattr(args, "func"):
        args.func(args)
    else:
        main_parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
