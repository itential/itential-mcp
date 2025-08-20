# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pathlib
import importlib
import importlib.util

import ipsdk

from ipsdk.platform import AsyncPlatform

from . import config


class PlatformClient(object):

    def __init__(self):
        self.client = self._init_client()
        self._init_plugins()

    def _init_client(self) -> AsyncPlatform:
        """
        Initializes the client connection to Itential Platform

        Args:
            None

        Returns:
            AsyncPlatform: An instance of AsyncPlatform

        Raises:
            None
        """
        cfg = config.get()
        return ipsdk.platform_factory(want_async=True, **cfg.platform)

    def _init_plugins(self):
        """
        Dynamically loads service plugins from the services directory.

        Discovers and imports Python modules from the services directory,
        instantiates their Service classes, and registers them as attributes
        on the client instance.

        Args:
            None

        Returns:
            None

        Raises:
            ImportError: If a service module cannot be loaded
            AttributeError: If a service module lacks a Service class
        """
        services_path = pathlib.Path(__file__).resolve().parent / "services"

        # Early return if services directory doesn't exist
        if not services_path.exists():
            return

        # Get Python files, excluding private modules and __pycache__
        python_files = [
            f for f in services_path.iterdir()
            if f.is_file() and f.suffix == ".py" and not f.name.startswith("_")
        ]

        # Import and register services
        for module_file in python_files:
            module_name = module_file.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_file)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if module has Service class
                if not hasattr(module, "Service"):
                    continue

                service_instance = module.Service(self.client)
                setattr(self, service_instance.name, service_instance)

            except (ImportError, AttributeError, Exception):
                # Log error but continue loading other services
                # Consider adding proper logging here in the future
                continue
