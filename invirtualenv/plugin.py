# Copyright (c) 2016, Yahoo Inc.
# Copyrights licensed under the BSD License
# See the accompanying LICENSE.txt file for terms.

"""
Functions to enable packaging plugin functionality
"""
import logging
import pkg_resources
from .utility import update_recursive, csv_list


logger = logging.getLogger(__name__)  # pylint: disable=C0103


CONFIG_DEFAULT = """[global]
name =
basepython =
install_manifest =
install_os_packages = False
version =
virtualenv_dir =
virtualenv_deploy_dir=
virtualenv_version_package =
virtualenv_user =
virtualenv_group =

[pip]
deps:

[rpm]
fail_missing_yum = True
deps:

"""
CONFIG_TYPES = {
    'global': {
        'install_manifest': csv_list,
        'install_os_packages': bool
    },
    'pip': {
        'deps': list
    },
    'rpm': {
        'deps': list,
        'fail_missing_yum': bool
    },
}


def package_formats():
    """
    Get a list of all the supported package types

    Returns
    -------
    list
        A list of supported package type strings
    """
    supported_types = []
    for entry_point in pkg_resources.iter_entry_points(
            group='invirtualenv.supported'
    ):  # pragma: no cover
        supported = entry_point.load()
        logger.debug(supported)
        supported_types += supported()
    supported_types.sort()
    logger.debug('Supported package types: %s', supported_types)
    return supported_types


def config():
    """
    Get default configuration settings for all installed plugins

    Returns
    -------
    str
        Configparser format configuration as a string
    dict
        Configuration types dictionary
    """
    config_string = CONFIG_DEFAULT
    config_types_dict = CONFIG_TYPES
    for entry_point in pkg_resources.iter_entry_points(
            group='invirtualenv.config'
    ):  # pragma: no cover
        default_config_function = entry_point.load()
        default_config, default_types = default_config_function()
        if default_config:
            logger.debug('Adding to default config: %r', default_config)
            config_string += default_config
        if default_types:
            logger.debug('Adding to default types: %r', default_types)
            config_types_dict = update_recursive(
                config_types_dict, default_types
            )

    return config_string, config_types_dict


def config_update(configuration):
    """
    Allow plugins to update the configuration after the values have been
    propagated.

    This function updates the dictionary in place.

    Parameters
    ----------
    configuration : dict
        The configuration dictionary
    """
    for entry_point in pkg_resources.iter_entry_points(
            group='invirtualenv.config_update'
    ):  # pragma: no cover
        config_update_function = entry_point.load()
        config_update_function(configuration)

    logger.debug('Updated configuration: %r', configuration)


def config_defaults():
    """
    Get default configuration settings for all installed plugins

    Returns
    -------
    str
        ConfigParser format configuration as a string
    """
    return config()[0]


def config_types():
    """
    Get the default types for all configuration valuse based on installed
    plugins.

    Returns
    -------
    dict
        Dictionary with configuration values as keys and object classes as
        values
    """
    return config()[1]


def create_package(package_type):
    """
    Create a package of a specific package type

    This functions iterates all the registered invirtualenv.create_package
    entry points and runs them passing the package_type argument to them.

    These plugins should return None if they do not handle that package type.

    Parameters
    ----------
    package_type : str
        The package type to create a package for

    """
    for entry_point in pkg_resources.iter_entry_points(
            group='invirtualenv.create_package'
    ):
        package = entry_point.load()
        package_name = package(package_type)
        if package_name:
            return package(package_type)

    return None
