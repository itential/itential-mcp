# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from typing import Any

from ipsdk.platform import AsyncPlatform

from abc import ABC, abstractmethod

class ServiceBase(ABC):
    """Abstract base class for Itential Platform service implementations.
    
    ServiceBase provides a common interface and foundation for all service
    classes that interact with the Itential Platform. Services are responsible
    for encapsulating specific API operations and providing a clean interface
    for tool implementations to consume platform resources.
    
    All concrete service implementations must inherit from this class and
    implement the abstract describe method. The class maintains a reference
    to the platform client for making API requests.
    
    Args:
        client: An AsyncPlatform client instance for communicating with
            the Itential Platform API
            
    Attributes:
        client (AsyncPlatform): The platform client used for API communication
    """

    def __init__(self, client: AsyncPlatform):
        self.client = client

    @abstractmethod
    async def describe(self, *args, **kwargs) -> Any | None:
        """
        Abstract method used to describe a server resource

        This method is an abstract method that will provide detailed
        information about a resource from the server.  All services
        should implement this method.

        Args:
            *args: Tuple of positional arguments passed to the method
            **kwargs: Keywork arguments passed to the method as a dict

        Returns:
            Any: Returns an object to the calling function.  The
                implementation may return None
        """
        pass


