# OAuth Authentication

The Itential MCP server supports OAuth authentication to secure access to the server and its tools. This document provides comprehensive guidance on configuring and using OAuth authentication with the MCP server.

## Overview

The MCP server's `server.auth.type` setting recognizes two OAuth-related modes:

1. **OAuth Provider** (`oauth`) - Intended to act as a full OAuth authorization server. **Not currently supported** -- see [OAuth Provider Mode](#oauth-provider-mode-not-currently-supported) below. Setting `auth_type` to `oauth` always raises `ConfigurationException` at startup.
2. **OAuth Proxy** (`oauth_proxy`) - Proxies authentication to upstream OAuth providers (Google, Azure, Auth0, GitHub, Okta). This is the supported, working OAuth mode.

Both modes require HTTP-based transports (`sse` or `http`) and are incompatible with the `stdio` transport.

## Configuration Options

OAuth authentication is configured through environment variables, command line arguments, or configuration files. All OAuth settings use the `server_auth_oauth_` prefix.

### Common OAuth Settings

| Environment Variable | CLI Option | Description |
|---------------------|------------|-------------|
| `ITENTIAL_MCP_SERVER_AUTH_TYPE` | `--auth-type` | Set to `oauth_proxy` (supported) or `jwt`. `oauth` is also a recognized value but is **not currently supported** -- it always raises `ConfigurationException` at startup; see [OAuth Provider Mode](#oauth-provider-mode-not-currently-supported) |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID` | `--auth-oauth-client-id` | OAuth client ID |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET` | `--auth-oauth-client-secret` | OAuth client secret |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI` | `--auth-oauth-redirect-uri` | OAuth callback/redirect URI |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES` | `--auth-oauth-scopes` | OAuth scopes (space or comma separated) |

### OAuth Provider Settings

> **Not currently supported.** Full OAuth server mode (`oauth`) always raises `ConfigurationException` at startup -- see [OAuth Provider Mode](#oauth-provider-mode-not-currently-supported). The settings below are documented only so that users encountering the exception understand what the (currently non-functional) mode would have configured. Use [OAuth Proxy Mode](#oauth-proxy-mode) instead.

| Environment Variable | CLI Option | Description |
|---------------------|------------|-------------|
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI` | `--auth-oauth-redirect-uri` | **Required** - Redirect URI for OAuth callbacks |

### OAuth Proxy Settings

For OAuth proxy mode (`oauth_proxy`):

| Environment Variable | CLI Option | Description |
|---------------------|------------|-------------|
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL` | `--auth-oauth-authorization-url` | **Required** - Upstream authorization endpoint |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL` | `--auth-oauth-token-url` | **Required** - Upstream token endpoint |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_USERINFO_URL` | `--auth-oauth-userinfo-url` | Optional - Upstream user info endpoint |
| `ITENTIAL_MCP_SERVER_AUTH_JWKS_URI` | `--auth-jwks-uri` | **Required** (one of `jwks_uri` or `public_key`) - JWKS endpoint for verifying upstream tokens |
| `ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY` | `--auth-public-key` | **Required** (one of `jwks_uri` or `public_key`) - Static public key/secret for verifying upstream tokens |

## OAuth Provider Mode (Not Currently Supported)

**`auth_type = oauth` (full OAuth authorization server mode) is not currently supported.** Setting `ITENTIAL_MCP_SERVER_AUTH_TYPE` (or `--auth-type`) to `oauth` always raises `ConfigurationException` at server startup.

Full authorization-server mode needs a user/credential store and Platform identity verification, which is tracked under the per-user "on behalf of" work. Rather than accept configuration that cannot complete a real handshake, the server fails fast at startup with a clear error.

**If you need OAuth authentication today, use [OAuth Proxy Mode](#oauth-proxy-mode) instead**, which delegates authentication to a real upstream identity provider (Google, Azure, Auth0, GitHub, Okta, or a generic provider) and is fully supported.


## OAuth Issuer and One-Time Re-authorization

In OAuth proxy mode the authorization-server issuer (and the `iss` claim of tokens the server issues) tracks the server's public base URL, which is the `scheme://netloc` derived from `ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI`. If you change the public URL (host, port, or scheme), the issuer and `iss` change with it and existing clients must re-authorize once.

## OAuth Proxy Mode

The OAuth proxy mode delegates authentication to external OAuth providers while maintaining control over token validation and user sessions.

### Token Verification Requirement

OAuth proxy mode validates tokens issued by the upstream provider using a `JWTVerifier`. Because the MCP server itself never issues these tokens, it needs a way to verify their signatures independently -- either by fetching signing keys dynamically from the provider's JWKS endpoint, or by checking against a static public key/secret. At least one of `ITENTIAL_MCP_SERVER_AUTH_JWKS_URI` (`--auth-jwks-uri`) or `ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY` (`--auth-public-key`) is therefore **required** when `auth_type` is `oauth_proxy`. If neither is set, the server raises a `ConfigurationException` at startup rather than proceeding without a way to validate tokens.

### Supported Providers

Example configurations for popular OAuth providers:

#### Google OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-google-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-google-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://accounts.google.com/o/oauth2/auth"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://oauth2.googleapis.com/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
```

**Default scopes for Google:** `openid email profile`

#### Azure AD OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-azure-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-azure-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://login.microsoftonline.com/common/oauth2/v2.0/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
# Replace {tenant} with your Azure AD tenant ID, or "common" for multi-tenant apps
export ITENTIAL_MCP_SERVER_AUTH_JWKS_URI="https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys"
```

**Default scopes for Azure:** `openid email profile`

#### GitHub OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-github-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-github-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://github.com/login/oauth/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://github.com/login/oauth/access_token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
```

**Note:** GitHub OAuth access tokens are opaque strings, not JWTs, and GitHub does not
publish a JWKS endpoint for verifying them. `oauth_proxy` mode requires a `JWTVerifier`
(configured via `ITENTIAL_MCP_SERVER_AUTH_JWKS_URI` or `ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY`),
so GitHub's standard OAuth token flow is not directly compatible with this mode as
documented here. If you need to front GitHub authentication with `oauth_proxy`, you must
put an identity layer in front of it that issues verifiable JWTs (for example, GitHub
Apps' OIDC-based flows or a third-party identity broker) and point `jwks_uri` at that
layer's JWKS endpoint instead of a GitHub URL.

**Default scopes for GitHub:** `user:email`

#### Auth0 OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-auth0-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-auth0-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://your-domain.auth0.com/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://your-domain.auth0.com/oauth/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
export ITENTIAL_MCP_SERVER_AUTH_JWKS_URI="https://your-domain.auth0.com/.well-known/jwks.json"
```

**Default scopes for Auth0:** `openid email profile`

#### Okta OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-okta-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-okta-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://your-domain.okta.com/oauth2/default/v1/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://your-domain.okta.com/oauth2/default/v1/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
export ITENTIAL_MCP_SERVER_AUTH_JWKS_URI="https://your-domain.okta.com/oauth2/default/v1/keys"
```

**Default scopes for Okta:** `openid email profile`

#### Generic OAuth Provider
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://provider.example.com/oauth/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://provider.example.com/oauth/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_USERINFO_URL="https://provider.example.com/oauth/userinfo"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="openid email profile"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
# Replace with your provider's actual JWKS endpoint
export ITENTIAL_MCP_SERVER_AUTH_JWKS_URI="https://provider.example.com/.well-known/jwks.json"
```

**Note:** Generic providers require explicit scope configuration.

## Scope Configuration

OAuth scopes define the permissions requested from the OAuth provider. Scopes can be specified in multiple formats:

### Space-Separated Scopes
```bash
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="openid email profile"
```

### Comma-Separated Scopes
```bash
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="openid,email,profile"
```

### Mixed Separators
```bash
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="openid, email profile,user:read"
```

The server automatically normalizes all scope formats into a consistent list.

## Transport Compatibility

OAuth authentication modes have specific transport requirements:

| Auth Type | stdio | sse | http |
|-----------|-------|-----|------|
| `oauth` (not currently supported) | ❌ | ❌ | ❌ |
| `oauth_proxy` | ❌ | ✅ | ✅ |
| `jwt` | ✅ | ✅ | ✅ |

OAuth requires HTTP-based transports because it needs to handle redirect URLs and callback endpoints. `oauth` is listed here for completeness only -- it always raises `ConfigurationException` at startup regardless of transport; see [OAuth Provider Mode](#oauth-provider-mode-not-currently-supported).

## Complete Examples

### Google OAuth with SSE Transport

```bash
# Set up Google OAuth with Server-Sent Events transport
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="123456789.apps.googleusercontent.com"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-google-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://accounts.google.com/o/oauth2/auth"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://oauth2.googleapis.com/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="openid email profile"
export ITENTIAL_MCP_SERVER_AUTH_JWKS_URI="https://www.googleapis.com/oauth2/v3/certs"

# Start the server
itential-mcp --transport sse --host 0.0.0.0 --port 8000
```

### Azure AD with Custom Scopes

```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-azure-app-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-azure-app-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="https://your-domain.com/auth/callback"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="https://graph.microsoft.com/User.Read openid email profile"
export ITENTIAL_MCP_SERVER_AUTH_JWKS_URI="https://login.microsoftonline.com/your-tenant-id/discovery/v2.0/keys"

itential-mcp --transport sse --host 0.0.0.0 --port 8000
```

## Authentication Flow

1. **Client initiates authentication** - Client makes a request to the MCP server
2. **Server redirects to OAuth provider** - Server redirects to the configured authorization URL
3. **User authenticates** - User logs in via the OAuth provider's interface
4. **Provider redirects back** - OAuth provider redirects to the configured callback URI
5. **Server validates tokens** - MCP server validates the returned tokens
6. **Session established** - Authenticated session is established for subsequent requests

## Troubleshooting

### Common Configuration Errors

**`auth_type = oauth` is not supported:**
```
ConfigurationException: Full OAuth authorization server mode ('oauth') is not currently supported (dynamic client registration cannot persist registered clients). Use 'oauth_proxy' to delegate authentication to an upstream OAuth provider instead.
```
If you see this error, you set `ITENTIAL_MCP_SERVER_AUTH_TYPE` (or `--auth-type`) to `oauth`. This mode always fails at startup -- see [OAuth Provider Mode](#oauth-provider-mode-not-currently-supported). Switch to `oauth_proxy` and configure an upstream identity provider as shown in [OAuth Proxy Mode](#oauth-proxy-mode).

**Missing required fields:**
```
ConfigurationException: OAuth proxy authentication requires the following fields: client_id, client_secret, authorization_url, token_url, redirect_uri
```

**Missing token verifier:**
```
ConfigurationException: OAuth proxy authentication requires a token verifier: set jwks_uri or public_key
```

**Transport compatibility:**
```
OAuth providers only support HTTP-based transports (sse, http), not stdio
```

### Debugging OAuth Issues

1. **Enable debug logging:**
   ```bash
   export ITENTIAL_MCP_SERVER_LOG_LEVEL="DEBUG"
   ```

2. **Verify provider endpoints:** Ensure authorization and token URLs are correct for your OAuth provider

3. **Check redirect URI registration:** Verify the redirect URI is registered with your OAuth provider

4. **Validate client credentials:** Confirm client ID and secret are correct and have proper permissions

## Security Considerations

1. **Use HTTPS in production:** Always use HTTPS for redirect URIs in production environments
2. **Secure client secrets:** Store client secrets securely using environment variables or secret management systems
3. **Validate scopes:** Only request the minimum scopes necessary for your application
4. **Regular credential rotation:** Rotate OAuth credentials regularly as part of security best practices

## Integration with AI Assistants

When using OAuth authentication with AI assistants, ensure your assistant configuration includes the authentication details. See the [AI Assistant Configuration Guide](ai-assistant-configs.md) for platform-specific setup instructions.