# Configuration reference

The Itential MCP server provides a number of different options for
configuration.  Below is a list of the available configuration options.  All
configuration options can also be specified using environment variables.

To configure any setting using environment variables, preface the configuration
setting with `ITENTIAL_MCP_<key>`.  For instance, to set the value for
`transport` to `sse`, use `ITENTIAL_MCP_TRANSPORT=sse` or to set the value of
`platform-host` to `platform.itential.dev`, use
`ITENTIAL_MCP_PLATFORM_HOST=platform.itential.dev`

If a value is configured using both an environment variable and a command line
option, the envrionment variable takes precedence.

## MCP Server

The configuration settings in this section apply to the running the MCP server.

### `transport`

Configures the MCP transport to use when starting the MCP server.  Valid values
include `stdio` and `sse`.  The default value is `sse`.

### `host`

Configures the host or address to listen for connections on.  This
configuration setting only applies if the value for `transport` is set to `sse`.
The default value is `localhost`

### `port`

Configures the port to listen for connections on.  This configuration setting
only applies if the value for `transport` is `sse`.  The default value is
`8000`

### `log_level`

Configures the logging level of the MCP server.  Valid values for setting the
logging level are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.  The default
value is `INFO`


## Itential Platform

The configuraiton settings in this section apply configuring the connection to
Itential Platform

### `platform-host`

The hostname or IP address of the Itential Platform server to connect to.  The
default value is `localhost`

### `platform-port`

The port value to use when connecting to the Itential Platform server.  When
this value is set to `0`, the port value is automatically determined.  The
default value is `0`

### `platform-disable-tls`

Disable the use of TLS for the connection.  When this option is used and the
port value is set to `0`, the port value will automatically be set to `80`,
otherwise it will be set to `443`.

### `platform-disable-verify`

This option will disable the certificate verification for the connection.  This
is useful when using self-signed certificates.

### `platform-user`

The username to use when authenticating to Itential Platform using basic
authentication.  If both `platform-client-id` and `platform-client-secret` are
used, this value is ignored.  The default value is `admin`.

### `platform-password`

The password to use when authentiating to Itential Platform.  If both
`platform-client-id` and `platform-client-secret` are used, this value is
ignored.  The default value is `admin`.

### `platform-client-id`

The client ID to send when authenticating to Itential Platform using OAuth.

### `platform-client-secret`

The client secret to send when authenticating to Itential Platform using OAuth.
