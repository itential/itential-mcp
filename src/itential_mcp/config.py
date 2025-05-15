# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from . import env


def get() -> dict:
    """
    Load the configuration from the environment

    This function will load the Platform configuration from the environment
    and return it as a Python dict object.  The returned object can be passed
    into the `platform_factory(...)` function to create a new instance.

    Args:
        None

    Returns:
        dict: Returns a Python dict object that represents the configuration

    Raises:
        None
    """
    return {
        "host": env.getstr("PLATFORM_HOST", default="localhost"),
        "port": env.getint("PLATFORM_PORT", default=0),

        "use_tls": not env.getbool("PLATFORM_DISABLE_TLS", default=False),
        "verify": not env.getbool("PLATFORM_DISABLE_VERFITY", default=False),

        "user": env.getstr("PLATFORM_USER", default="admin"),
        "password": env.getstr("PLATFORM_PASSWORD", default="admin"),

        "client_id": env.getstr("PLATFORM_CLIENT_ID"),
        "client_secret": env.getstr("PLATFORM_CLIENT_SECRET"),
    }
