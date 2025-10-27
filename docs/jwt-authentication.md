# JWT Authentication Guide

This guide explains how to enable JSON Web Token (JWT) authentication for the
Itential MCP server and configure the available validation options. By default
the server launches without authentication (`--auth-type none`). Supplying the
JWT options described below instructs FastMCP to wrap every request in a token
check before exposing any tools.

## Prerequisites

Before switching the server to JWT mode, gather the following details from your
identity provider:

- A JWKS endpoint _or_ a PEM encoded public key/shared secret that can validate
  issued tokens.
- The expected issuer (`iss`) claim.
- Optionally, the audience (`aud`) values and any scopes that must be present on
  incoming tokens.

All values can come from command line options, environment variables, or an
`mcp.conf` file. Configuration precedence is Environment > CLI arguments >
configuration file > built-in defaults.

## Quick Start (CLI)

Start the MCP server with JWT enforcement by providing `--auth-type jwt` plus
either a JWKS URI or a static key:

```bash
itential-mcp \
  --auth-type jwt \
  --auth-jwks-uri https://idp.example.com/.well-known/jwks.json \
  --auth-issuer https://idp.example.com/ \
  --auth-audience itential-mcp \
  --auth-required-scopes mcp.read,mcp.write
```

Use `--auth-public-key` when you want to embed a PEM or HMAC secret instead of a
JWKS lookup:

```bash
itential-mcp \
  --auth-type jwt \
  --auth-public-key "$(cat /etc/keys/mcp.pub)" \
  --auth-issuer internal-idp \
  --auth-algorithm RS256
```

The server fails to start if the JWT verifier cannot initialize with the
supplied settings, producing a configuration error describing the problem.

## Using `mcp.conf`

The same values can be stored in the `[server]` section of an `mcp.conf` file so
you do not need to repeat them on the CLI:

```ini
[server]
auth_type = jwt
auth_jwks_uri = https://idp.example.com/.well-known/jwks.json
auth_issuer = https://idp.example.com/
auth_audience = itential-mcp,another-client
auth_required_scopes = mcp.read,mcp.write
```

Point the server at the config file with `itential-mcp --config /path/to/mcp.conf`.
You can override individual values by passing CLI flags or exporting the matching
environment variables.

## Environment Variables

Environment variables use the `ITENTIAL_MCP_SERVER_AUTH_` prefix and can be
combined with CLI flags or config files:

| Purpose | Environment variable | CLI flag |
|---------|---------------------|----------|
| Enable JWT | `ITENTIAL_MCP_SERVER_AUTH_TYPE=jwt` | `--auth-type jwt` |
| JWKS endpoint | `ITENTIAL_MCP_SERVER_AUTH_JWKS_URI` | `--auth-jwks-uri` |
| Static public key/secret | `ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY` | `--auth-public-key` |
| Expected issuer (`iss`) | `ITENTIAL_MCP_SERVER_AUTH_ISSUER` | `--auth-issuer` |
| Expected audience (`aud`) | `ITENTIAL_MCP_SERVER_AUTH_AUDIENCE` | `--auth-audience` |
| Signing algorithm | `ITENTIAL_MCP_SERVER_AUTH_ALGORITHM` | `--auth-algorithm` |
| Required scopes | `ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES` | `--auth-required-scopes` |

Audience and scope values accept comma separated lists. The configuration layer
converts them into lists before passing them to the FastMCP `JWTVerifier`.

## Validation Behavior

- Provide **exactly one** of `--auth-jwks-uri` or `--auth-public-key`. The JWT
  verifier loads remote keys when a JWKS URI is supplied and falls back to a
  static key otherwise.
- `--auth-issuer` and `--auth-audience` are optional but strongly recommended.
  The verifier rejects tokens whose `iss` or `aud` claims do not match.
- Use `--auth-algorithm` to restrict accepted signing algorithms (for example
  `RS256`, `HS256`). Leave it unset to allow whatever the FastMCP verifier
  supports for the provided key.
- The `--auth-required-scopes` list enforces presence of each scope in the JWT
  `scope` (space separated string) or `scp` (array) claims.

Once JWT authentication is enabled, unauthenticated requests and requests with
invalid tokens receive HTTP 401 responses and no tools are exposed until a valid
token is presented.

