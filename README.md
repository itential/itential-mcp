# itenial-mcp

The `itential-mcp` application provides a MCP server for connecting to Itential
Platform.  The MCP server exposes a set of tools that can be attached to an LLM
and used when reasoning out responses.

## Installation

The `itential-mcp` application can be installed using either PyPI or it can be
run directly from source.

To install it from PyPI, simply use `pip`:

```bash
$ pip install itential-mcp
```

The repository can also be clone the repository to your local environment to
work with the MCP server.   The project uses `uv` and `make` so both tools
would need to be installed and available in your environment.

The following commands can be used to get started.

```bash
$ git clone https://github.com/itential/itential-mcp
$ cd itential-mcp
$ make build
```

## Running the server

The MCP server can be invoked by either using the command line or by running it
as a container.  The server supports either `stdio` (default) or `sse`
transport.

To start the server using the command line when it has been installed, simply
run `itential-mcp`.

To start the server using `sse` as the transport, the command would be
`itential-mcp --transport sse`.

The MCP server can also be run as a container.  If you have cloned the
repository to your local environment and have `make` installed, there is a
target for building the container.  Simply run `make container` from the root
of the repository.

## Configuring the server

The MCP server configuration can be passed via the command line using
`itential-mcp` and specifying one or more command line options.   Run
`itential-mcp --help` for usage details.

All configuration options can also be passed using environment variables.
Environment variables take precedence over configuration options passed on the
command line.

The environment variables should be used for passing configuration into the
container.

See the [configuration reference](docs/configuration-reference.md) for details
about the avaiable configuration options.

## License

This project is licensed under the GPLv3 open source license.  See
[license](LICENSE)
