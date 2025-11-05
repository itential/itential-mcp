# OAuth Authentication

The Itential MCP server supports OAuth authentication to secure access to the server and its tools. This document provides comprehensive guidance on configuring and using OAuth authentication with the MCP server.

## Overview

The MCP server supports two OAuth authentication modes:

1. **OAuth Provider** - Acts as a full OAuth authorization server
2. **OAuth Proxy** - Proxies authentication to upstream OAuth providers (Google, Azure, Auth0, GitHub, Okta)

Both modes require HTTP-based transports (`sse` or `http`) and are incompatible with the `stdio` transport.

## Configuration Options

OAuth authentication is configured through environment variables, command line arguments, or configuration files. All OAuth settings use the `server_auth_oauth_` prefix.

### Common OAuth Settings

| Environment Variable | CLI Option | Description |
|---------------------|------------|-------------|
| `ITENTIAL_MCP_SERVER_AUTH_TYPE` | `--auth-type` | Set to `oauth` or `oauth_proxy` |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID` | `--auth-oauth-client-id` | OAuth client ID |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET` | `--auth-oauth-client-secret` | OAuth client secret |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI` | `--auth-oauth-redirect-uri` | OAuth callback/redirect URI |
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES` | `--auth-oauth-scopes` | OAuth scopes (space or comma separated) |

### OAuth Provider Settings

For full OAuth server mode (`oauth`):

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
| `ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE` | `--auth-oauth-provider-type` | Provider type: `google`, `azure`, `auth0`, `github`, `okta`, `generic` |

## OAuth Provider Mode

The OAuth provider mode turns the MCP server into a full OAuth authorization server. This is useful when you want the MCP server to handle authentication directly.

### Configuration

**Environment Variables:**
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="openid email profile"
```

**Command Line:**
```bash
itential-mcp --transport sse \
  --auth-type oauth \
  --auth-oauth-redirect-uri "http://localhost:8000/auth/callback" \
  --auth-oauth-scopes "openid email profile"
```

**Configuration File:**
```ini
[server]
auth_type = oauth
auth_oauth_redirect_uri = http://localhost:8000/auth/callback
auth_oauth_scopes = openid email profile
```

### Base URL Derivation

The OAuth provider automatically derives the base URL from the redirect URI by removing the `/auth/callback` suffix:

- **Redirect URI:** `http://localhost:8000/auth/callback`
- **Base URL:** `http://localhost:8000`

## OAuth Proxy Mode

The OAuth proxy mode delegates authentication to external OAuth providers while maintaining control over token validation and user sessions.

### Supported Providers

The MCP server includes predefined configurations for popular OAuth providers:

#### Google OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE="google"
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
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE="azure"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-azure-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-azure-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://login.microsoftonline.com/common/oauth2/v2.0/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
```

**Default scopes for Azure:** `openid email profile`

#### GitHub OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE="github"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-github-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-github-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://github.com/login/oauth/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://github.com/login/oauth/access_token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
```

**Default scopes for GitHub:** `user:email`

#### Auth0 OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE="auth0"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-auth0-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-auth0-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://your-domain.auth0.com/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://your-domain.auth0.com/oauth/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
```

**Default scopes for Auth0:** `openid email profile`

#### Okta OAuth
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE="okta"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-okta-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-okta-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://your-domain.okta.com/oauth2/default/v1/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://your-domain.okta.com/oauth2/default/v1/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
```

**Default scopes for Okta:** `openid email profile`

#### Generic OAuth Provider
```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE="generic"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-client-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://provider.example.com/oauth/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://provider.example.com/oauth/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_USERINFO_URL="https://provider.example.com/oauth/userinfo"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="openid email profile"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
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
| `oauth` | ❌ | ✅ | ✅ |
| `oauth_proxy` | ❌ | ✅ | ✅ |
| `jwt` | ✅ | ✅ | ✅ |

OAuth requires HTTP-based transports because it needs to handle redirect URLs and callback endpoints.

## Complete Examples

### Google OAuth with SSE Transport

```bash
# Set up Google OAuth with Server-Sent Events transport
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE="google"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="123456789.apps.googleusercontent.com"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-google-client-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://accounts.google.com/o/oauth2/auth"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://oauth2.googleapis.com/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="http://localhost:8000/auth/callback"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="openid email profile"

# Start the server
itential-mcp --transport sse --host 0.0.0.0 --port 8000
```

### OAuth Provider Mode with Configuration File

**config.ini:**
```ini
[server]
transport = sse
host = 0.0.0.0
port = 8000
auth_type = oauth
auth_oauth_redirect_uri = http://localhost:8000/auth/callback
auth_oauth_scopes = openid email profile

[platform]
host = platform.example.com
user = admin
password = admin
```

**Start the server:**
```bash
export ITENTIAL_MCP_CONFIG="config.ini"
itential-mcp
```

### Azure AD with Custom Scopes

```bash
export ITENTIAL_MCP_SERVER_AUTH_TYPE="oauth_proxy"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE="azure"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID="your-azure-app-id"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET="your-azure-app-secret"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL="https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/authorize"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL="https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/token"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI="https://your-domain.com/auth/callback"
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES="https://graph.microsoft.com/User.Read openid email profile"

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

**Missing required fields:**
```
ConfigurationException: OAuth proxy authentication requires the following fields: client_id, client_secret, authorization_url, token_url, redirect_uri
```

**Transport compatibility:**
```
OAuth providers only support HTTP-based transports (sse, http), not stdio
```

**Invalid redirect URI:**
```
The redirect URI must end with /auth/callback for automatic base URL derivation
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