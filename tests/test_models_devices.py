# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.devices import (
    Device,
    GetDevicesResponse,
    GetDeviceConfigurationResponse,
    BackupDeviceConfigurationResponse,
    ApplyDeviceConfigurationResponse,
)


class TestDevice:
    """Test cases for Device model."""

    def test_device_valid_creation(self):
        """Test that Device can be created with valid data."""
        device_data = {
            "name": "router-1",
            "host": "192.168.1.1",
            "deviceType": "cisco_ios",
            "status": "active",
        }

        device = Device(**device_data)

        assert device.name == "router-1"
        assert device.host == "192.168.1.1"
        assert device.deviceType == "cisco_ios"
        assert device.status == "active"

    def test_device_with_extra_fields(self):
        """Test that Device allows extra fields."""
        device_data = {
            "name": "router-1",
            "host": "192.168.1.1",
            "deviceType": "cisco_ios",
            "status": "active",
            "location": "datacenter-a",
            "vendor": "cisco",
        }

        device = Device(**device_data)

        assert device.name == "router-1"
        assert device.location == "datacenter-a"
        assert device.vendor == "cisco"

    def test_device_missing_optional_fields(self):
        """Test that Device allows missing optional fields with default values."""
        device_data = {
            "name": "router-1",
            "host": "192.168.1.1",
            # Missing deviceType and status - should default to None
        }

        device = Device(**device_data)

        assert device.name == "router-1"
        assert device.host == "192.168.1.1"
        assert device.deviceType is None
        assert device.status is None


class TestGetDevicesResponse:
    """Test cases for GetDevicesResponse model."""

    def test_get_devices_response_empty_list(self):
        """Test that GetDevicesResponse can handle empty list."""
        response = GetDevicesResponse([])

        assert response.root == []
        assert len(response.root) == 0

    def test_get_devices_response_single_device(self):
        """Test that GetDevicesResponse can handle single device."""
        device_data = {
            "name": "router-1",
            "host": "192.168.1.1",
            "deviceType": "cisco_ios",
            "status": "active",
        }

        response = GetDevicesResponse([device_data])

        assert len(response.root) == 1
        assert response.root[0].name == "router-1"

    def test_get_devices_response_multiple_devices(self):
        """Test that GetDevicesResponse can handle multiple devices."""
        devices_data = [
            {
                "name": "router-1",
                "host": "192.168.1.1",
                "deviceType": "cisco_ios",
                "status": "active",
            },
            {
                "name": "switch-1",
                "host": "192.168.1.2",
                "deviceType": "cisco_ios",
                "status": "inactive",
            },
        ]

        response = GetDevicesResponse(devices_data)

        assert len(response.root) == 2
        assert response.root[0].name == "router-1"
        assert response.root[1].name == "switch-1"


class TestGetDeviceConfigurationResponse:
    """Test cases for GetDeviceConfigurationResponse model."""

    def test_get_device_configuration_response(self):
        """Test that GetDeviceConfigurationResponse can handle string config."""
        config = "interface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0"

        response = GetDeviceConfigurationResponse(config)

        assert response.root == config
        assert "interface GigabitEthernet0/0" in response.root

    def test_get_device_configuration_response_empty(self):
        """Test that GetDeviceConfigurationResponse can handle empty config."""
        response = GetDeviceConfigurationResponse("")

        assert response.root == ""


class TestBackupDeviceConfigurationResponse:
    """Test cases for BackupDeviceConfigurationResponse model."""

    def test_backup_device_configuration_response_valid(self):
        """Test that BackupDeviceConfigurationResponse can be created with valid data."""
        backup_data = {
            "id": "backup-123",
            "status": "success",
            "message": "Backup created successfully",
        }

        response = BackupDeviceConfigurationResponse(**backup_data)

        assert response.id == "backup-123"
        assert response.status == "success"
        assert response.message == "Backup created successfully"

    def test_backup_device_configuration_response_with_extra_fields(self):
        """Test that BackupDeviceConfigurationResponse allows extra fields."""
        backup_data = {
            "id": "backup-123",
            "status": "success",
            "message": "Backup created successfully",
            "timestamp": "2025-01-01T00:00:00Z",
            "size": 1024,
        }

        response = BackupDeviceConfigurationResponse(**backup_data)

        assert response.id == "backup-123"
        assert response.timestamp == "2025-01-01T00:00:00Z"
        assert response.size == 1024

    def test_backup_device_configuration_response_missing_required_fields(self):
        """Test that BackupDeviceConfigurationResponse validation fails with missing fields."""
        backup_data = {
            "id": "backup-123",
            # Missing status and message
        }

        with pytest.raises(ValidationError):
            BackupDeviceConfigurationResponse(**backup_data)


class TestApplyDeviceConfigurationResponse:
    """Test cases for ApplyDeviceConfigurationResponse model."""

    def test_apply_device_configuration_response_allows_any_fields(self):
        """Test that ApplyDeviceConfigurationResponse allows any fields."""
        apply_data = {
            "result": "success",
            "jobId": "job-456",
            "message": "Configuration applied successfully",
            "timestamp": "2025-01-01T00:00:00Z",
            "device": "router-1",
        }

        response = ApplyDeviceConfigurationResponse(**apply_data)

        assert response.result == "success"
        assert response.jobId == "job-456"
        assert response.message == "Configuration applied successfully"
        assert response.timestamp == "2025-01-01T00:00:00Z"
        assert response.device == "router-1"

    def test_apply_device_configuration_response_empty(self):
        """Test that ApplyDeviceConfigurationResponse can be created empty."""
        response = ApplyDeviceConfigurationResponse()

        # Should not raise any errors
        assert isinstance(response, ApplyDeviceConfigurationResponse)
