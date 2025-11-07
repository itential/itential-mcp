# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions of Itential MCP:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Itential MCP, please report it responsibly.

### How to Report

**Please do NOT create public GitHub issues for security vulnerabilities.**

Instead, please report security vulnerabilities through one of the following methods:

1. **Email**: Send details to opensource@itential.com
2. **Private vulnerability disclosure**: Use GitHub's private vulnerability reporting feature

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes or mitigations
- Your contact information for follow-up

### Response Timeline

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Updates**: We will provide regular updates on our progress every 7 days
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

## Security Best Practices

### For Users

When deploying Itential MCP:

1. **Authentication**: Always configure proper authentication credentials
2. **Network Security**:
   - Use HTTPS/TLS for all communications
   - Restrict network access to authorized users only
   - Consider using VPNs or private networks
3. **Credentials Management**:
   - Use environment variables for sensitive configuration
   - Never commit credentials to version control
   - Rotate credentials regularly
4. **Updates**: Keep Itential MCP and its dependencies up to date
5. **Monitoring**: Implement logging and monitoring for security events

### For Contributors

When contributing to Itential MCP:

1. **Code Review**: All code changes require review before merging
2. **Dependencies**:
   - Keep dependencies up to date
   - Use dependency scanning tools
   - Avoid adding unnecessary dependencies
3. **Input Validation**: Always validate and sanitize user inputs
4. **Error Handling**: Avoid exposing sensitive information in error messages
5. **Testing**: Include security-focused test cases
6. **Documentation**: Document security implications of new features

## Security Architecture

### Transport Security

- **stdio**: Inherits security context of the parent process
- **SSE/HTTP**: Supports HTTPS/TLS encryption
- **Authentication**: Integration with Itential Platform authentication

### Data Handling

- **Credentials**: Stored securely using environment variables or secure credential stores
- **API Communication**: All API calls to Itential Platform use authenticated sessions
- **Logging**: Sensitive data is not logged or is properly redacted

### Dependencies

- Regular dependency updates through automated tooling
- Security scanning of dependencies
- Minimal dependency footprint to reduce attack surface

## Vulnerability Disclosure Policy

### Coordinated Disclosure

We follow a coordinated disclosure approach:

1. **Private Notification**: Vulnerabilities are first reported privately
2. **Investigation**: We investigate and develop fixes
3. **Testing**: Fixes are thoroughly tested
4. **Release**: Security updates are released
5. **Public Disclosure**: Details are disclosed after fixes are available

### Recognition

We appreciate security researchers who follow responsible disclosure practices. With your permission, we will:

- Acknowledge your contribution in release notes
- Include you in our security hall of fame
- Provide swag or other recognition as appropriate

## Security Contact

For security-related questions or to report vulnerabilities:

- **General Security Questions**: [to be configured]
- **Vulnerability Reports**: Use private disclosure methods described above

## Updates to This Policy

This security policy may be updated from time to time. Changes will be announced through:

- Repository release notes
- Security advisories
- Project communication channels

---

**Note**: This policy is effective as of the date it was added to the repository and applies to all versions of Itential MCP.
