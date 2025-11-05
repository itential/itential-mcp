# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ipsdk.platform import AsyncPlatform


class ServiceBase(object):
    """Abstract base class for Itential Platform service implementations.

    ServiceBase provides a common interface and foundation for all service
    classes that interact with the Itential Platform. Services are responsible
    for encapsulating specific API operations and providing a clean interface
    for tool implementations to consume platform resources.

    Args:
        client: An AsyncPlatform client instance for communicating with
            the Itential Platform API

    Attributes:
        client (AsyncPlatform): The platform client used for API communication
    """

    def __init__(self, client: AsyncPlatform):
        self.client = client
