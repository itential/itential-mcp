# TLS Configuration for Itential MCP Server

This document describes how to configure TLS (Transport Layer Security) for the Itential MCP server to enable secure connections between clients and the server.

## Overview

The Itential MCP server supports TLS encryption for secure communication when using network-based transports (`sse` or `http`). TLS is not applicable when using the `stdio` transport as it communicates through standard input/output streams.

## Prerequisites

Before enabling TLS, you need:

1. A valid TLS certificate file (`.pem` or `.crt` format)
2. The corresponding private key file (`.pem` or `.key` format)
3. The server configured to use either `sse` or `http` transport

## Generating Self-Signed Certificates (Development Only)

For development and testing purposes, you can generate self-signed certificates using OpenSSL:

```bash
# Generate a private key
openssl genrsa -out server.key 2048

# Generate a self-signed certificate
openssl req -new -x509 -key server.key -out server.crt -days 365 -subj "/CN=localhost"

# Convert to PEM format if needed
openssl x509 -in server.crt -out server.pem -outform PEM
```

**Warning**: Self-signed certificates should never be used in production environments as they do not provide proper identity verification.

## Production Certificates

For production deployments, obtain certificates from a trusted Certificate Authority (CA) such as:
- Let's Encrypt (free)
- DigiCert
- Sectigo
- Your organization's internal CA

## Configuration Methods

### Method 1: Configuration File

Add the TLS settings to your MCP configuration file:

```ini
[server]
transport = sse
host = 0.0.0.0
port = 8443
certificate_file = /path/to/server.pem
private_key_file = /path/to/server.key
```

### Method 2: Environment Variables

Set the TLS configuration using environment variables:

```bash
export ITENTIAL_MCP_SERVER_TRANSPORT=sse
export ITENTIAL_MCP_SERVER_HOST=0.0.0.0
export ITENTIAL_MCP_SERVER_PORT=8443
export ITENTIAL_MCP_SERVER_CERTIFICATE_FILE=/path/to/server.pem
export ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE=/path/to/server.key
```

### Method 3: Command Line Arguments

Pass TLS settings directly via command line:

```bash
itential-mcp --transport sse --host 0.0.0.0 --port 8443 \
  --certificate-file /path/to/server.pem \
  --private-key-file /path/to/server.key
```

## Certificate File Requirements

### Certificate File
- Must be in PEM format
- Should contain the server certificate and any intermediate certificates
- File extension can be `.pem`, `.crt`, or `.cert`
- Must be readable by the user running the MCP server

### Private Key File
- Must be in PEM format
- Should contain the private key corresponding to the certificate
- File extension can be `.pem`, `.key`, or `.private`
- Must be readable by the user running the MCP server
- Should have restricted permissions (e.g., `chmod 600`)

### Example Certificate Chain File
```
-----BEGIN CERTIFICATE-----
[Your server certificate]
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
[Intermediate certificate 1]
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
[Intermediate certificate 2]
-----END CERTIFICATE-----
```

## File Permissions and Security

Ensure proper file permissions for security:

```bash
# Set restrictive permissions on private key
chmod 600 /path/to/server.key

# Certificate can be more permissive but still secure
chmod 644 /path/to/server.pem

# Ensure proper ownership
chown mcp-user:mcp-group /path/to/server.key /path/to/server.pem
```

## Testing TLS Configuration

### 1. Start the Server
```bash
itential-mcp --transport sse --certificate-file server.pem --private-key-file server.key
```

### 2. Test with curl
```bash
# Test HTTPS connectivity
curl -k https://localhost:8000/mcp

# For production with valid certificates (remove -k flag)
curl https://your-domain.com:8000/mcp
```

### 3. Verify Certificate Details
```bash
# Check certificate information
openssl x509 -in server.pem -text -noout

# Test TLS connection
openssl s_client -connect localhost:8000 -servername localhost
```

## Common Port Configurations

| Transport | Default Port | Common TLS Port | Purpose |
|-----------|--------------|-----------------|---------|
| `sse`     | 8000         | 8443           | Server-Sent Events over HTTPS |
| `http`    | 8000         | 8443           | HTTP API over HTTPS |
| `stdio`   | N/A          | N/A            | Standard I/O (no network) |

## Troubleshooting

### Certificate/Key Mismatch
```
Error: certificate and private key do not match
```
**Solution**: Verify the certificate and private key are a matching pair:
```bash
# Compare certificate and key fingerprints
openssl x509 -noout -modulus -in server.pem | openssl md5
openssl rsa -noout -modulus -in server.key | openssl md5
```

### Permission Denied
```
Error: permission denied reading certificate file
```
**Solutions**:
- Check file permissions: `ls -la /path/to/certificate/files`
- Ensure the MCP server user has read access
- Verify file ownership and group membership

### Certificate Expired
```
Error: certificate has expired
```
**Solutions**:
- Check certificate validity: `openssl x509 -in server.pem -noout -dates`
- Obtain and install a new certificate
- For Let's Encrypt, use `certbot renew`

### Hostname Mismatch
```
Error: certificate hostname does not match
```
**Solutions**:
- Ensure certificate Common Name (CN) or Subject Alternative Name (SAN) matches the hostname
- Use the correct hostname when connecting
- For development, add the hostname to your `/etc/hosts` file

## Client Configuration

When TLS is enabled, clients must connect using HTTPS:

### MCP Client Configuration
```json
{
  "servers": {
    "itential": {
      "command": "curl",
      "args": ["-X", "POST", "https://your-server:8443/mcp"]
    }
  }
}
```

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "itential": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "https://your-server:8443/mcp"
      ]
    }
  }
}
```

## Security Best Practices

1. **Use Strong Certificates**: Obtain certificates from trusted CAs for production
2. **Regular Rotation**: Rotate certificates before expiration
3. **Secure Key Storage**: Store private keys with restrictive permissions
4. **Monitor Expiration**: Set up monitoring for certificate expiration dates
5. **Use Strong Ciphers**: The server uses secure TLS configurations by default
6. **Regular Updates**: Keep the MCP server updated for security patches
7. **Network Security**: Use firewalls and network segmentation as additional layers

## Integration with Reverse Proxies

For production deployments, consider using a reverse proxy like nginx or Apache for TLS termination:

### nginx Configuration Example
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/server.pem;
    ssl_certificate_key /path/to/server.key;
    
    location /mcp {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

This approach allows the reverse proxy to handle TLS while the MCP server runs with standard HTTP transport.