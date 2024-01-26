# main function here

import os
from logger import log
import argparse
from TravHarvConfigBuilder import TravHarvConfigBuilder
from TravHarvExecuter import TravHarvExecutor

# log = logging.getLogger(__name__)


def get_arg_parser():
    """
    Get the argument parser for the module
    """
    parser = argparse.ArgumentParser(
        description="pyTravHarv", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print verbose output"
    )

    parser.add_argument(
        "-cf",
        "--config-folder",
        type=str,
        default=os.path.join(os.getcwd(), "config"),
        help="Folder containing configuration files, relative to the folder or file this was called from",
    )

    parser.add_argument(
        "-n", "--name", type=str, default=None, help="Name of the configuration to use"
    )

    parser.add_argument(
        "-o",
        "--output-folder",
        type=str,
        default=os.path.join(os.getcwd(), "output"),
        help="Folder to output files to",
    )

    parser.add_argument(
        "-ts",
        "--target-store",
        type=str,
        default=None,
        help="Target store to harvest, this can be a pointer to a triple store in memory or the base URI of a triple store",
    )

    parser.add_argument(
        "-l",
        "--logconf",
        type=str,
        action="store",
        help="location of the logging config (yml) to use",
    )

    return parser


def main():
    """
    The main entrypoint of the module
    """
    args = get_arg_parser().parse_args()
    log.debug(args)

    # make different classes here to use
    # TargetStore
    # TravHarvExecutor
    # TravHarvConfigBuilder
    travharv_config_builder = TravHarvConfigBuilder(args.config_folder)

    if args.name is None:
        travharv_config_builder.build_from_folder()
    else:
        travharv_config_builder.build_from_config(args.name)

    # some logging to see if the config is built correctly
    log.info("Config object: {}".format(travharv_config_builder.travHarvConfig))

    for config_file, config in travharv_config_builder.travHarvConfig.items():
        log.info("Config file: {}".format(config_file))
        log.info("Config: {}".format(config))
        travharvexecutor = TravHarvExecutor(
            config_file, config["prefix_set"], config["tasks"]
        )

    # log the prefix mappings | SubjectDefinition and AssertionPathSet here
    log.info(travharv_config_builder.travHarvConfig["base_test.yml"].keys())
    tasks = travharv_config_builder.travHarvConfig["base_test.yml"]["tasks"]

    for task in tasks:
        todotas = task.get_task()
        log.info("Task: {}".format(todotas))

        assertpathset = todotas["assert_path_set"]

        log.info("AssertionPathSet: {}".format(assertpathset.get_assert_path_set()))
        assertionPathSetObject = assertpathset.get_assert_path_set()

        for assertionPath in assertionPathSetObject:
            log.info("AssertionPath size: {}".format(assertionPath.get_max_size()))
            log.info(
                "AssertionPath at depth size-1: {}".format(
                    assertionPath.get_path_for_depth(assertionPath.get_max_size() - 0)
                )
            )


if __name__ == "__main__":
    main()
