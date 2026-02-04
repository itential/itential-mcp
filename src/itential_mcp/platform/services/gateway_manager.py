# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from typing import Sequence, Mapping, Any

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """
    Gateway Manager service for interacting with Itential Platform Gateway Manager.

    Gateway Manager is a distributed orchestration system that manages remote
    gateways and the services they provide. It enables execution of external
    tools (Ansible playbooks, Terraform scripts, Python scripts, etc.) across
    multiple clusters in a distributed environment. This service provides
    comprehensive management capabilities for gateways, services, certificates,
    and service groups.

    Key capabilities:
        - Gateway lifecycle management (create, read, update, delete)
        - Service discovery and execution across distributed clusters
        - Certificate management for secure gateway communication
        - Service group organization for logical grouping
        - Connection health monitoring and status tracking
        - Version and health check endpoints

    Attributes:
        name (str): The service name identifier "gateway_manager"
    """

    name: str = "gateway_manager"

    async def get_services(self) -> Sequence[Mapping[str, Any]]:
        """
        Retrieve all available services from all connected gateways.

        Services represent executable capabilities provided by gateways, such as
        Ansible playbooks, Terraform plans, Python scripts, or other external
        tools. This method returns a comprehensive list of all services across
        all registered gateways and clusters.

        Returns:
            Sequence[Mapping[str, Any]]: List of service objects, each containing:
                - id: Unique service identifier
                - name: Service name
                - cluster_id: The cluster this service belongs to
                - gateway_id: The gateway hosting this service
                - type: Service type (ansible, terraform, python, etc.)
                - description: Human-readable service description
                - enabled: Whether the service is available for execution
                - parameters: Expected input parameters for service execution

        Raises:
            HTTPError: If the API request fails
            ConnectionException: If unable to connect to Gateway Manager

        Example:
            services = await client.gateway_manager.get_services()
            for service in services:
                print(f"{service['name']} on {service['cluster_id']}")
        """
        res = await self.client.get("/gateway_manager/v1/services")
        json_data = res.json()
        return json_data["result"]

    async def get_gateways(self) -> Sequence[Mapping[str, Any]]:
        """
        Retrieve all registered gateways from Gateway Manager.

        Gateways are remote agents that connect to the Itential Platform and
        provide access to external services and tools. Each gateway can host
        multiple services and belongs to a specific cluster. This method returns
        all gateways regardless of their connection status, allowing you to view
        both active and inactive gateways.

        Returns:
            Sequence[Mapping[str, Any]]: List of gateway objects, each containing:
                - id: Unique gateway identifier
                - name: Human-readable gateway name
                - cluster_id: The cluster identifier this gateway belongs to
                - description: Detailed description of the gateway's purpose
                - status: Connection status (connected, disconnected, error)
                - enabled: Whether the gateway is enabled and available for use
                - version: Gateway agent version
                - last_seen: Timestamp of last successful connection
                - services_count: Number of services provided by this gateway
                - created_at: Gateway registration timestamp
                - updated_at: Last modification timestamp

        Raises:
            HTTPError: If the API request fails
            ConnectionException: If unable to connect to Gateway Manager

        Example:
            gateways = await client.gateway_manager.get_gateways()
            active_gateways = [g for g in gateways if g["status"] == "connected"]
            print(f"Found {len(active_gateways)} active gateways")
        """
        res = await self.client.get("/gateway_manager/v1/gateways")
        return res.json()

    async def get_service(self, service_id: str) -> Mapping[str, Any]:
        """
        Retrieve detailed information about a specific service.

        Fetches comprehensive metadata about a service, including its
        configuration, parameters, execution history, and current status.
        This is useful for validating service availability and understanding
        required inputs before executing the service.

        Args:
            service_id (str): The unique identifier of the service to retrieve

        Returns:
            Mapping[str, Any]: Detailed service object containing:
                - id: Unique service identifier
                - name: Service name
                - type: Service type (ansible, terraform, python, shell, etc.)
                - cluster_id: Associated cluster identifier
                - gateway_id: Gateway hosting this service
                - description: Detailed service description
                - enabled: Whether the service is available for execution
                - parameters: Schema of expected input parameters
                - environment: Environment variables required
                - timeout: Maximum execution time in seconds
                - retry_policy: Retry configuration for failed executions
                - last_execution: Timestamp of most recent execution
                - execution_count: Total number of times service has been run
                - success_rate: Percentage of successful executions
                - created_at: Service registration timestamp
                - updated_at: Last modification timestamp

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the service doesn't exist
            AuthorizationException: If user lacks permission to view the service

        Example:
            service = await client.gateway_manager.get_service("svc_123abc")
            print(f"Service: {service['name']}")
            print(f"Required params: {service['parameters']}")
        """
        res = await self.client.get(f"/gateway_manager/v1/services/{service_id}")
        return res.json()

    async def run_service(
        self, name: str, cluster: str, *, input_params: dict | None = None
    ) -> Mapping[str, Any]:
        """
        Execute a service on a remote gateway with optional input parameters.

        This method triggers synchronous execution of a service (Ansible playbook,
        Terraform plan, Python script, etc.) on the specified gateway cluster.
        The call blocks until the service completes execution and returns the
        full execution results including stdout, stderr, and return code.

        For long-running services, consider the timeout configuration of both
        the service and the API client. Services that exceed their configured
        timeout will be terminated automatically.

        Args:
            name (str): The name of the service to execute (not the service ID)
            cluster (str): The cluster identifier where the service should run
            input_params (dict | None): Optional dictionary of input parameters
                required by the service. Parameter names and types must match
                the service's parameter schema. Defaults to None.

        Returns:
            Mapping[str, Any]: Execution result object containing:
                - execution_id: Unique identifier for this execution
                - service_name: Name of the executed service
                - cluster_id: Cluster where execution occurred
                - gateway_id: Gateway that executed the service
                - status: Execution status (success, failure, timeout)
                - stdout: Standard output captured from the service
                - stderr: Standard error output captured from the service
                - return_code: Exit code returned by the service (0 = success)
                - start_time: ISO 8601 timestamp when execution started
                - end_time: ISO 8601 timestamp when execution completed
                - elapsed_time: Execution duration in seconds
                - input_params: Parameters that were provided to the service
                - error_message: Detailed error message if execution failed

        Raises:
            HTTPError: If the API request fails
            ValidationException: If service name, cluster, or parameters are invalid
            NotFoundError: If the service or cluster doesn't exist
            TimeoutExceededError: If service execution exceeds timeout
            ServiceUnavailableException: If the gateway is not connected
            AuthorizationException: If user lacks permission to execute the service

        Example:
            result = await client.gateway_manager.run_service(
                name="deploy_configuration",
                cluster="production",
                input_params={
                    "device_name": "router01",
                    "config_template": "basic_bgp",
                    "variables": {"asn": 65001}
                }
            )
            if result["return_code"] == 0:
                print(f"Success: {result['stdout']}")
            else:
                print(f"Failed: {result['stderr']}")
        """
        body = {
            "serviceName": name,
            "clusterId": cluster,
        }

        if input_params:
            body["params"] = input_params

        res = await self.client.post("/gateway_manager/v1/services/run", json=body)

        return res.json()

    async def get_certificates(self) -> Sequence[Mapping[str, Any]]:
        """
        Retrieve all SSL/TLS certificates registered in Gateway Manager.

        Certificates are used to secure communication between the Itential
        Platform and remote gateways. This method returns all certificates
        regardless of their status, including expired and revoked certificates.

        Returns:
            Sequence[Mapping[str, Any]]: List of certificate objects, each containing:
                - id: Unique certificate identifier
                - contract_id: Contract identifier for the certificate
                - alias: Human-readable certificate alias
                - subject: Certificate subject (CN, O, OU, etc.)
                - issuer: Certificate issuer information
                - valid_from: Certificate validity start date (ISO 8601)
                - valid_to: Certificate expiration date (ISO 8601)
                - is_expired: Boolean indicating if certificate is expired
                - fingerprint: Certificate SHA-256 fingerprint
                - serial_number: Certificate serial number
                - created_at: Registration timestamp
                - updated_at: Last modification timestamp

        Raises:
            HTTPError: If the API request fails
            ConnectionException: If unable to connect to Gateway Manager

        Example:
            certs = await client.gateway_manager.get_certificates()
            for cert in certs:
                if cert["is_expired"]:
                    print(f"WARNING: Certificate {cert['alias']} has expired")
        """
        res = await self.client.get("/gateway_manager/v1/certificates")
        return res.json()

    async def create_certificate(
        self, raw_certificate: str, contract_id: str, *, alias: str | None = None
    ) -> Mapping[str, Any]:
        """
        Register a new SSL/TLS certificate for gateway authentication.

        Uploads and registers a certificate that can be used to establish
        secure connections between gateways and the Itential Platform. The
        certificate must be in PEM format and should be a valid X.509
        certificate signed by a trusted certificate authority.

        Args:
            raw_certificate (str): The complete certificate in PEM format,
                including the BEGIN and END certificate markers. Should be
                URL-encoded if necessary. Example:
                "-----BEGIN CERTIFICATE-----\nMIID..."
            contract_id (str): Unique identifier for this certificate contract,
                used to reference this certificate in gateway configurations
            alias (str | None): Optional human-readable name for the certificate
                to make it easier to identify. Defaults to None.

        Returns:
            Mapping[str, Any]: The created certificate object containing:
                - id: Assigned unique identifier
                - contract_id: The provided contract identifier
                - alias: Certificate alias (if provided)
                - subject: Parsed certificate subject information
                - issuer: Certificate issuer details
                - valid_from: Certificate validity start date
                - valid_to: Certificate expiration date
                - fingerprint: SHA-256 fingerprint of the certificate
                - created_at: Registration timestamp

        Raises:
            HTTPError: If the API request fails
            ValidationException: If certificate data is malformed, expired,
                or not in valid PEM format
            ConflictException: If a certificate with the same contract_id
                already exists

        Example:
            with open("gateway_cert.pem", "r") as f:
                cert_data = f.read()

            result = await client.gateway_manager.create_certificate(
                raw_certificate=cert_data,
                contract_id="prod_gateway_cert_001",
                alias="Production Gateway Certificate"
            )
            print(f"Certificate registered with ID: {result['id']}")
        """
        body = {
            "raw_certificate": raw_certificate,
            "contract_id": contract_id,
        }

        if alias:
            body["alias"] = alias

        res = await self.client.post("/gateway_manager/v1/certificates", json=body)
        return res.json()

    async def get_certificate(self, certificate_id: str) -> Mapping[str, Any]:
        """
        Retrieve detailed information about a specific certificate.

        Fetches complete metadata for a certificate, including validity
        dates, subject information, and usage statistics. This is useful
        for auditing certificate usage and checking expiration dates.

        Args:
            certificate_id (str): The unique identifier of the certificate

        Returns:
            Mapping[str, Any]: Detailed certificate object containing:
                - id: Unique certificate identifier
                - contract_id: Contract identifier
                - alias: Human-readable certificate name
                - raw_certificate: The original PEM-encoded certificate
                - subject: Certificate subject (CN, O, OU, C, ST, L)
                - issuer: Certificate authority information
                - valid_from: Validity start date (ISO 8601)
                - valid_to: Expiration date (ISO 8601)
                - is_expired: Whether the certificate has expired
                - fingerprint: SHA-256 fingerprint
                - serial_number: Certificate serial number
                - key_usage: Certificate key usage extensions
                - gateways_using: List of gateway IDs using this certificate
                - created_at: Registration timestamp
                - updated_at: Last modification timestamp

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the certificate doesn't exist
            AuthorizationException: If user lacks permission to view certificate

        Example:
            cert = await client.gateway_manager.get_certificate("cert_123abc")
            days_until_expiry = (
                datetime.fromisoformat(cert["valid_to"]) - datetime.now()
            ).days
            if days_until_expiry < 30:
                print(f"WARNING: Certificate expires in {days_until_expiry} days")
        """
        res = await self.client.get(
            f"/gateway_manager/v1/certificates/{certificate_id}"
        )
        return res.json()

    async def update_certificate(
        self,
        certificate_id: str,
        *,
        alias: str | None = None,
        contract_id: str | None = None,
        raw_certificate: str | None = None,
    ) -> Mapping[str, Any]:
        """
        Update certificate metadata or replace the certificate data.

        Allows updating certificate properties such as alias or contract_id,
        or replacing the certificate data itself (for certificate rotation).
        Note that updating the raw certificate will affect all gateways
        currently using this certificate.

        Args:
            certificate_id: The unique identifier of the certificate to update.
            alias: New human-readable name. Defaults to None.
            contract_id: New contract identifier. Defaults to None.
            raw_certificate: Replacement certificate in PEM format. Defaults to None.

        Returns:
            Mapping[str, Any]: The updated certificate object with all current values

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the certificate doesn't exist
            ValidationException: If update data is invalid or new certificate
                data is malformed
            ConflictException: If the new contract_id conflicts with an existing
                certificate

        Example:
            updated = await client.gateway_manager.update_certificate(
                certificate_id="cert_123abc",
                alias="Production Gateway Certificate - Renewed"
            )
            print(f"Certificate updated: {updated['alias']}")
        """
        body = {}
        if alias is not None:
            body["alias"] = alias
        if contract_id is not None:
            body["contract_id"] = contract_id
        if raw_certificate is not None:
            body["raw_certificate"] = raw_certificate

        res = await self.client.put(
            f"/gateway_manager/v1/certificates/{certificate_id}", json=body
        )
        return res.json()

    async def delete_certificate(self, certificate_id: str) -> Mapping[str, Any]:
        """
        Remove a certificate from Gateway Manager.

        Permanently deletes a certificate from the system. This operation will
        fail if the certificate is currently in use by any gateway. You must
        first update all gateways to use a different certificate before deletion.

        Args:
            certificate_id (str): The unique identifier of the certificate to delete

        Returns:
            Mapping[str, Any]: Deletion confirmation containing:
                - success: Boolean indicating successful deletion
                - message: Confirmation message
                - deleted_at: Timestamp of deletion

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the certificate doesn't exist
            ConflictException: If the certificate is currently in use by one
                or more gateways
            AuthorizationException: If user lacks permission to delete certificates

        Example:
            try:
                result = await client.gateway_manager.delete_certificate("cert_123abc")
                print(f"Certificate deleted successfully")
            except ConflictException:
                print("Cannot delete: certificate is in use by gateways")
        """
        res = await self.client.delete(
            f"/gateway_manager/v1/certificates/{certificate_id}"
        )
        return res.json()

    async def get_connections(self) -> Sequence[Mapping[str, Any]]:
        """
        Retrieve all active gateway connections and their current status.

        Returns only gateways that are currently connected and actively
        communicating with the Itential Platform. This is useful for
        determining which gateways are available for service execution
        and monitoring the overall health of your distributed infrastructure.

        Returns:
            Sequence[Mapping[str, Any]]: List of active connection objects, each containing:
                - cluster_id: Unique cluster identifier
                - gateway_id: Gateway identifier within the cluster
                - gateway_name: Human-readable gateway name
                - status: Connection status (typically "connected" for active connections)
                - connection_time: ISO 8601 timestamp when connection was established
                - last_heartbeat: Timestamp of most recent heartbeat
                - uptime: Connection duration in seconds
                - ip_address: Remote IP address of the gateway
                - version: Gateway agent software version
                - services_available: Number of services provided by this gateway
                - active_executions: Number of currently running service executions

        Raises:
            HTTPError: If the API request fails
            ConnectionException: If unable to connect to Gateway Manager

        Example:
            connections = await client.gateway_manager.get_connections()
            print(f"Active gateways: {len(connections)}")
            for conn in connections:
                print(f"  {conn['gateway_name']}: {conn['services_available']} services")
        """
        res = await self.client.get("/gateway_manager/v1/connections")
        return res.json()

    async def get_connection(self, cluster_id: str) -> Mapping[str, Any]:
        """
        Check the health and status of a specific gateway connection.

        Performs a health check on a gateway connection to verify that the
        gateway is reachable, responsive, and ready to execute services.
        This is useful for pre-flight checks before executing critical
        services or for monitoring and alerting purposes.

        Args:
            cluster_id (str): The cluster identifier to check connection health for

        Returns:
            Mapping[str, Any]: Connection health status object containing:
                - cluster_id: The checked cluster identifier
                - gateway_id: Associated gateway identifier
                - gateway_name: Gateway name
                - is_healthy: Boolean indicating overall health status
                - status: Detailed status (connected, disconnected, error, degraded)
                - connection_time: When the current connection was established
                - last_heartbeat: Timestamp of most recent heartbeat
                - uptime: Current connection duration in seconds
                - latency_ms: Round-trip latency in milliseconds
                - services_available: Number of available services
                - active_executions: Currently running executions
                - error_message: Detailed error if health check failed
                - checked_at: Timestamp of this health check

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the cluster doesn't exist or has never connected
            ConnectionException: If unable to reach the gateway

        Example:
            health = await client.gateway_manager.get_connection("prod_cluster_01")
            if health["is_healthy"]:
                print(f"Gateway healthy (latency: {health['latency_ms']}ms)")
            else:
                print(f"Gateway unhealthy: {health['error_message']}")
        """
        res = await self.client.get(f"/gateway_manager/v1/connections/{cluster_id}")
        return res.json()

    async def create_gateway(
        self,
        cluster_id: str,
        name: str,
        description: str,
        enabled: bool,
        *,
        certificate_id: str | None = None,
        connection_config: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """
        Register a new gateway in Gateway Manager.

        Creates a gateway configuration that a remote gateway agent can use
        to connect to the Itential Platform. After creating the gateway
        configuration, you must configure and start the corresponding gateway
        agent with the connection details and authentication credentials.

        Args:
            cluster_id: Unique identifier for the cluster (must be unique).
            name: Human-readable gateway name.
            description: Detailed description of the gateway's purpose.
            enabled: Whether the gateway is enabled (true/false).
            certificate_id: ID of certificate for TLS authentication. Defaults to None.
            connection_config: Custom connection settings. Defaults to None.
            tags: List of tags for organization and filtering. Defaults to None.
            metadata: Additional custom metadata. Defaults to None.

        Returns:
            Mapping[str, Any]: The created gateway object containing:
                - id: Assigned unique gateway identifier
                - cluster_id: The provided cluster identifier
                - name: Gateway name
                - description: Gateway description
                - enabled: Whether the gateway is enabled
                - status: Initial status (typically "disconnected")
                - connection_token: Authentication token for gateway agent
                - connection_url: WebSocket URL for gateway to connect to
                - certificate_id: Associated certificate (if provided)
                - created_at: Registration timestamp
                - created_by: User who created the gateway

        Raises:
            HTTPError: If the API request fails
            ValidationException: If gateway data is missing required fields or invalid
            ConflictException: If a gateway with the same cluster_id already exists
            AuthorizationException: If user lacks permission to create gateways

        Example:
            gateway = await client.gateway_manager.create_gateway(
                cluster_id="prod_cluster_01",
                name="Production Data Center Gateway",
                description="Gateway for production network automation",
                enabled=True,
                tags=["production", "network"]
            )
            print(f"Gateway created: {gateway['id']}")
            print(f"Connection token: {gateway['connection_token']}")
        """
        body = {
            "cluster_id": cluster_id,
            "name": name,
            "description": description,
            "enabled": enabled,
        }

        if certificate_id is not None:
            body["certificate_id"] = certificate_id
        if connection_config is not None:
            body["connection_config"] = connection_config
        if tags is not None:
            body["tags"] = tags
        if metadata is not None:
            body["metadata"] = metadata

        res = await self.client.post("/gateway_manager/v1/gateways", json=body)
        return res.json()

    async def get_gateway(self, gateway_id: str) -> Mapping[str, Any]:
        """
        Retrieve detailed information about a specific gateway.

        Fetches comprehensive metadata about a gateway, including its
        configuration, connection status, service inventory, and usage
        statistics. This is useful for monitoring gateway health and
        understanding service availability.

        Args:
            gateway_id (str): The unique identifier of the gateway to retrieve

        Returns:
            Mapping[str, Any]: Detailed gateway object containing:
                - id: Unique gateway identifier
                - cluster_id: Cluster identifier
                - name: Human-readable gateway name
                - description: Detailed gateway description
                - status: Current connection status (connected, disconnected, error)
                - enabled: Whether the gateway is enabled and usable
                - version: Gateway agent software version
                - connection_time: When current connection was established
                - last_seen: Timestamp of last communication
                - uptime: Current connection duration in seconds
                - certificate_id: Associated certificate identifier
                - services: List of services provided by this gateway
                - service_groups: Service group memberships
                - total_executions: Lifetime execution count
                - successful_executions: Number of successful executions
                - failed_executions: Number of failed executions
                - tags: Associated tags
                - metadata: Custom metadata
                - created_at: Registration timestamp
                - updated_at: Last modification timestamp
                - created_by: User who created the gateway

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the gateway doesn't exist
            AuthorizationException: If user lacks permission to view gateway

        Example:
            gateway = await client.gateway_manager.get_gateway("gw_123abc")
            print(f"Gateway: {gateway['name']}")
            print(f"Status: {gateway['status']}")
            print(f"Services: {len(gateway['services'])}")
            if gateway['status'] == 'connected':
                print(f"Uptime: {gateway['uptime']} seconds")
        """
        res = await self.client.get(f"/gateway_manager/v1/gateways/{gateway_id}")
        return res.json()

    async def update_gateway(
        self,
        gateway_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        enabled: bool | None = None,
        certificate_id: str | None = None,
        connection_config: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """
        Update gateway configuration or properties.

        Allows modifying gateway settings such as name, description, enabled
        status, or associated certificate. Changes take effect immediately
        and will be applied to the connected gateway agent on its next
        heartbeat. Disabling a gateway will prevent new service executions
        but will not terminate currently running executions.

        Args:
            gateway_id: The unique identifier of the gateway to update.
            name: New human-readable name. Defaults to None.
            description: Updated description. Defaults to None.
            enabled: Enable or disable the gateway (true/false). Defaults to None.
            certificate_id: Change to a different certificate. Defaults to None.
            connection_config: Update connection settings. Defaults to None.
            tags: Update tag list. Defaults to None.
            metadata: Update custom metadata. Defaults to None.

        Returns:
            Mapping[str, Any]: The updated gateway object with all current values

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the gateway doesn't exist
            ValidationException: If update data is invalid
            ConflictException: If attempting to change cluster_id to one that already exists
            AuthorizationException: If user lacks permission to update gateway

        Example:
            updated = await client.gateway_manager.update_gateway(
                gateway_id="gw_123abc",
                description="Updated description",
                enabled=False,
                tags=["production", "network", "maintenance"]
            )
            print(f"Gateway updated: {updated['name']}")
            print(f"Status: {'enabled' if updated['enabled'] else 'disabled'}")
        """
        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if enabled is not None:
            body["enabled"] = enabled
        if certificate_id is not None:
            body["certificate_id"] = certificate_id
        if connection_config is not None:
            body["connection_config"] = connection_config
        if tags is not None:
            body["tags"] = tags
        if metadata is not None:
            body["metadata"] = metadata

        res = await self.client.put(
            f"/gateway_manager/v1/gateways/{gateway_id}", json=body
        )
        return res.json()

    async def delete_gateway(self, gateway_id: str) -> Mapping[str, Any]:
        """
        Remove a gateway from Gateway Manager.

        Permanently deletes a gateway configuration. Any connected gateway
        agent will be disconnected and will no longer be able to authenticate.
        This operation cannot be undone. All historical execution data for
        this gateway will be retained but the gateway itself cannot be
        recovered.

        IMPORTANT: This will terminate any active service executions on the
        gateway. Ensure no critical services are running before deletion.

        Args:
            gateway_id (str): The unique identifier of the gateway to delete

        Returns:
            Mapping[str, Any]: Deletion confirmation containing:
                - success: Boolean indicating successful deletion
                - message: Confirmation message
                - gateway_id: ID of the deleted gateway
                - deleted_at: Timestamp of deletion

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the gateway doesn't exist
            ConflictException: If the gateway is currently connected and has
                active service executions
            AuthorizationException: If user lacks permission to delete gateways

        Example:
            try:
                result = await client.gateway_manager.delete_gateway("gw_123abc")
                print(f"Gateway deleted successfully")
            except ConflictException:
                print("Cannot delete: gateway has active executions")
        """
        res = await self.client.delete(f"/gateway_manager/v1/gateways/{gateway_id}")
        return res.json()

    async def get_service_groups(self) -> Sequence[Mapping[str, Any]]:
        """
        Retrieve all service groups for organizing and managing services.

        Service groups provide logical organization for related services,
        making it easier to manage permissions, execute groups of services
        together, and organize services by function, environment, or team.
        This is particularly useful in large deployments with many services
        across multiple gateways.

        Returns:
            Sequence[Mapping[str, Any]]: List of service group objects, each containing:
                - id: Unique service group identifier
                - name: Human-readable group name
                - description: Detailed description of the group's purpose
                - services: List of service IDs belonging to this group
                - service_count: Number of services in the group
                - enabled: Whether the service group is enabled
                - tags: Tags for categorization and filtering
                - created_at: Group creation timestamp
                - updated_at: Last modification timestamp
                - created_by: User who created the group

        Raises:
            HTTPError: If the API request fails
            ConnectionException: If unable to connect to Gateway Manager

        Example:
            groups = await client.gateway_manager.get_service_groups()
            for group in groups:
                print(f"{group['name']}: {group['service_count']} services")
        """
        res = await self.client.get("/gateway_manager/v1/service-groups")
        return res.json()

    async def create_service_group(
        self,
        name: str,
        description: str,
        *,
        services: list[str] | None = None,
        enabled: bool | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """
        Create a new service group for organizing related services.

        Service groups help organize services logically, enabling bulk
        operations, simplified permission management, and better service
        discovery. You can group services by function (backup, deployment),
        environment (prod, staging), or team ownership.

        Args:
            name: Unique name for the service group.
            description: Detailed description of the group's purpose.
            services: List of service IDs to include in the group. Defaults to None.
            enabled: Whether the group is enabled (default: true). Defaults to None.
            tags: List of tags for categorization. Defaults to None.
            metadata: Custom metadata dictionary. Defaults to None.

        Returns:
            Mapping[str, Any]: The created service group object containing:
                - id: Assigned unique identifier
                - name: Service group name
                - description: Group description
                - services: List of included service IDs
                - service_count: Number of services in the group
                - enabled: Whether the group is enabled
                - tags: Associated tags
                - metadata: Custom metadata
                - created_at: Creation timestamp
                - created_by: User who created the group

        Raises:
            HTTPError: If the API request fails
            ValidationException: If required fields are missing or invalid
            ConflictException: If a service group with the same name already exists
            AuthorizationException: If user lacks permission to create service groups

        Example:
            group = await client.gateway_manager.create_service_group(
                name="network_deployment",
                description="Services for network device configuration deployment",
                services=["svc_123", "svc_456"],
                enabled=True,
                tags=["network", "deployment"]
            )
            print(f"Service group created: {group['id']}")
        """
        body = {
            "name": name,
            "description": description,
        }

        if services is not None:
            body["services"] = services
        if enabled is not None:
            body["enabled"] = enabled
        if tags is not None:
            body["tags"] = tags
        if metadata is not None:
            body["metadata"] = metadata

        res = await self.client.post(
            "/gateway_manager/v1/service-groups", json=body
        )
        return res.json()

    async def get_service_group(self, service_group_id: str) -> Mapping[str, Any]:
        """
        Retrieve detailed information about a specific service group.

        Fetches comprehensive metadata about a service group, including
        its member services, configuration, and usage statistics. This is
        useful for understanding service organization and managing group
        membership.

        Args:
            service_group_id (str): The unique identifier of the service group

        Returns:
            Mapping[str, Any]: Detailed service group object containing:
                - id: Unique service group identifier
                - name: Human-readable group name
                - description: Detailed description
                - services: List of service IDs in the group
                - service_details: Full service objects for each member
                - service_count: Number of services in the group
                - enabled: Whether the group is enabled
                - total_executions: Lifetime execution count across all services
                - tags: Associated tags
                - metadata: Custom metadata
                - created_at: Creation timestamp
                - updated_at: Last modification timestamp
                - created_by: User who created the group

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the service group doesn't exist
            AuthorizationException: If user lacks permission to view service group

        Example:
            group = await client.gateway_manager.get_service_group("sg_123abc")
            print(f"Service Group: {group['name']}")
            print(f"Services: {group['service_count']}")
            for service in group['service_details']:
                print(f"  - {service['name']}")
        """
        res = await self.client.get(
            f"/gateway_manager/v1/service-groups/{service_group_id}"
        )
        return res.json()

    async def update_service_group(
        self,
        service_group_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        services: list[str] | None = None,
        add_services: list[str] | None = None,
        remove_services: list[str] | None = None,
        enabled: bool | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """
        Update service group configuration or membership.

        Allows modifying service group properties or managing which services
        are members of the group. You can add or remove services, change the
        group's name or description, enable/disable the group, or update tags
        and metadata. Changes take effect immediately.

        Args:
            service_group_id: The unique identifier of the service group.
            name: New group name (must remain unique). Defaults to None.
            description: Updated description. Defaults to None.
            services: New list of service IDs (replaces existing). Defaults to None.
            add_services: List of service IDs to add to the group. Defaults to None.
            remove_services: List of service IDs to remove from the group. Defaults to None.
            enabled: Enable or disable the group. Defaults to None.
            tags: Update tag list. Defaults to None.
            metadata: Update custom metadata. Defaults to None.

        Returns:
            Mapping[str, Any]: The updated service group object with all current values

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the service group doesn't exist
            ValidationException: If update data is invalid or references non-existent services
            ConflictException: If attempting to change name to one that already exists
            AuthorizationException: If user lacks permission to update service group

        Example:
            updated = await client.gateway_manager.update_service_group(
                service_group_id="sg_123abc",
                description="Updated description",
                add_services=["svc_789"],
                tags=["network", "deployment", "production"]
            )
            print(f"Service group updated: {updated['name']}")
            print(f"Total services: {updated['service_count']}")
        """
        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if services is not None:
            body["services"] = services
        if add_services is not None:
            body["add_services"] = add_services
        if remove_services is not None:
            body["remove_services"] = remove_services
        if enabled is not None:
            body["enabled"] = enabled
        if tags is not None:
            body["tags"] = tags
        if metadata is not None:
            body["metadata"] = metadata

        res = await self.client.patch(
            f"/gateway_manager/v1/service-groups/{service_group_id}", json=body
        )
        return res.json()

    async def delete_service_group(self, service_group_id: str) -> Mapping[str, Any]:
        """
        Remove a service group from Gateway Manager.

        Permanently deletes a service group. This only removes the logical
        grouping - the services themselves remain available and are not
        affected. Any workflows or automation that reference this service
        group by ID will need to be updated after deletion.

        Args:
            service_group_id (str): The unique identifier of the service group to delete

        Returns:
            Mapping[str, Any]: Deletion confirmation containing:
                - success: Boolean indicating successful deletion
                - message: Confirmation message
                - service_group_id: ID of the deleted service group
                - deleted_at: Timestamp of deletion

        Raises:
            HTTPError: If the API request fails
            NotFoundError: If the service group doesn't exist
            AuthorizationException: If user lacks permission to delete service groups

        Example:
            result = await client.gateway_manager.delete_service_group("sg_123abc")
            print(f"Service group deleted successfully")
        """
        res = await self.client.delete(
            f"/gateway_manager/v1/service-groups/{service_group_id}"
        )
        return res.json()

    async def get_health_status(self) -> Mapping[str, Any]:
        """
        Perform a health check on Gateway Manager service.

        Returns the operational status of the Gateway Manager service itself,
        including connectivity to dependencies, resource usage, and overall
        health. This is useful for monitoring, alerting, and Kubernetes
        readiness/liveness probes.

        Returns:
            Mapping[str, Any]: Health status object containing:
                - status: Overall health status (healthy, degraded, unhealthy)
                - checks: Individual health check results
                - uptime: Service uptime in seconds
                - version: Gateway Manager version
                - timestamp: Health check timestamp

        Raises:
            HTTPError: If the API request fails

        Example:
            health = await client.gateway_manager.get_health_status()
            if health["status"] == "healthy":
                print(f"Gateway Manager is healthy (uptime: {health['uptime']}s)")
            else:
                print(f"Gateway Manager status: {health['status']}")
        """
        res = await self.client.get("/gateway_manager/v1/health/status")
        return res.json()

    async def get_version(self) -> Mapping[str, Any]:
        """
        Get the version information for Gateway Manager.

        Returns detailed version information about the Gateway Manager service,
        including the application version, build information, and supported
        API versions. This is useful for compatibility checking, troubleshooting,
        and ensuring you're using compatible client and server versions.

        Returns:
            Mapping[str, Any]: Version information object containing:
                - version: Semantic version (e.g., "2.1.0")
                - build: Build identifier or commit hash
                - api_version: Supported API version
                - build_date: ISO 8601 timestamp of when this version was built
                - supported_features: List of feature flags enabled

        Raises:
            HTTPError: If the API request fails

        Example:
            version = await client.gateway_manager.get_version()
            print(f"Gateway Manager version: {version['version']}")
            print(f"API version: {version['api_version']}")
        """
        res = await self.client.get("/gateway_manager/v1/version")
        return res.json()
