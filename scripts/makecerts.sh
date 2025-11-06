#!/usr/bin/env bash

# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# makecerts.sh - Generate development certificates using OpenSSL
#
# This script creates a self-signed CA and server certificate for development use.
# It generates RSA 4096-bit keys and configures certificates with proper extensions
# for TLS server authentication.

set -euo pipefail

# Configuration
readonly SCRIPT_NAME=$(basename "$0")
readonly CERT_DIR="certificates"
readonly CA_VALIDITY_DAYS=3650  # 10 years
readonly SERVER_VALIDITY_DAYS=825  # Chrome recommended limit
readonly KEY_SIZE=4096
readonly HASH_ALGO="sha256"

# Certificate subjects
readonly CA_SUBJECT="/CN=dev-local-CA"
readonly SERVER_SUBJECT="/CN=dev.local"

# Subject Alternative Names for server certificate
readonly SERVER_SAN="DNS:dev.local,DNS:localhost,IP:127.0.0.1"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Function to check if OpenSSL is available
check_dependencies() {
    if ! command -v openssl >/dev/null 2>&1; then
        log_error "OpenSSL is not installed or not in PATH"
        log_error "Please install OpenSSL and try again"
        exit 1
    fi
    
    local openssl_version
    openssl_version=$(openssl version)
    log_info "Using OpenSSL: $openssl_version"
}

# Function to setup certificate directory
setup_cert_directory() {
    log_info "Setting up certificate directory: $CERT_DIR"
    
    if [[ -d "$CERT_DIR" ]]; then
        log_warning "Certificate directory exists, removing it"
        rm -rf "$CERT_DIR"
    fi
    
    mkdir -p "$CERT_DIR"
    cd "$CERT_DIR"
    
    log_success "Certificate directory created"
}

# Function to generate CA private key and certificate
generate_ca() {
    log_info "Generating CA private key (RSA $KEY_SIZE bits)"
    
    openssl genrsa -out ca.key "$KEY_SIZE"
    
    # Set restrictive permissions on CA private key
    chmod 600 ca.key
    
    log_info "Generating self-signed CA certificate ($CA_VALIDITY_DAYS days validity)"
    
    openssl req -x509 -new -"$HASH_ALGO" -days "$CA_VALIDITY_DAYS" \
        -key ca.key -out ca.crt \
        -subj "$CA_SUBJECT" \
        -addext "basicConstraints=critical,CA:true,pathlen:1" \
        -addext "keyUsage=critical,keyCertSign,cRLSign" \
        -addext "subjectKeyIdentifier=hash"
    
    log_success "CA certificate generated: ca.crt"
}

# Function to generate server private key and CSR
generate_server_key_and_csr() {
    log_info "Generating server private key (RSA $KEY_SIZE bits)"
    
    openssl genrsa -out server.key "$KEY_SIZE"
    
    # Set restrictive permissions on server private key
    chmod 600 server.key
    
    log_info "Generating certificate signing request (CSR)"
    
    openssl req -new -"$HASH_ALGO" -key server.key -out server.csr.pem \
        -subj "$SERVER_SUBJECT" \
        -addext "subjectAltName=$SERVER_SAN" \
        -addext "keyUsage=digitalSignature,keyEncipherment" \
        -addext "extendedKeyUsage=serverAuth"
    
    log_success "Server CSR generated: server.csr.pem"
}

# Function to create server certificate extensions file
create_server_extensions() {
    log_info "Creating server certificate extensions file"
    
    cat > server.ext <<EOF
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=$SERVER_SAN
authorityKeyIdentifier=keyid,issuer
subjectKeyIdentifier=hash
EOF
    
    log_success "Server extensions file created: server.ext"
}

# Function to sign the server certificate
sign_server_certificate() {
    log_info "Signing server certificate with CA ($SERVER_VALIDITY_DAYS days validity)"
    
    openssl x509 -req -in server.csr.pem -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out server.crt -days "$SERVER_VALIDITY_DAYS" -"$HASH_ALGO" \
        -extfile server.ext
    
    log_success "Server certificate signed: server.crt"
}

# Function to verify the certificate chain
verify_certificates() {
    log_info "Verifying certificate chain"
    
    if openssl verify -CAfile ca.crt server.crt >/dev/null 2>&1; then
        log_success "Certificate chain verification passed"
    else
        log_error "Certificate chain verification failed"
        return 1
    fi
}

# Function to display certificate information
display_certificate_info() {
    log_info "Certificate information:"
    echo
    echo "=== CA Certificate ==="
    openssl x509 -in ca.crt -noout -text | grep -E "(Subject|Validity|Public Key)"
    echo
    echo "=== Server Certificate ==="
    openssl x509 -in server.crt -noout -text | grep -E "(Subject|Validity|Public Key|DNS:|IP Address:)"
}

# Function to cleanup temporary files
cleanup() {
    log_info "Cleaning up temporary files"
    rm -f server.csr.pem server.ext ca.srl
}

# Function to display usage information
usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Generate development certificates using OpenSSL.

This script creates:
- A self-signed CA certificate (ca.crt) and private key (ca.key)
- A server certificate (server.crt) and private key (server.key)
- Certificates are stored in the '$CERT_DIR' directory

Options:
  -h, --help     Show this help message
  -v, --verbose  Enable verbose output
  -q, --quiet    Suppress informational output

Examples:
  $SCRIPT_NAME           # Generate certificates with default settings
  $SCRIPT_NAME -v        # Generate certificates with verbose output
  $SCRIPT_NAME -q        # Generate certificates quietly

The generated certificates include:
- CA certificate valid for $CA_VALIDITY_DAYS days
- Server certificate valid for $SERVER_VALIDITY_DAYS days
- Server certificate includes SAN: $SERVER_SAN
EOF
}

# Function to handle script termination
cleanup_on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script terminated with error (exit code: $exit_code)"
    fi
}

# Main function
main() {
    local verbose=false
    local quiet=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Configure output based on options
    if [[ "$quiet" == true ]]; then
        exec 1>/dev/null
    fi
    
    if [[ "$verbose" == true ]]; then
        set -x
    fi
    
    # Set up exit trap
    trap cleanup_on_exit EXIT
    
    log_info "Starting certificate generation with $SCRIPT_NAME"
    
    # Execute certificate generation steps
    check_dependencies
    setup_cert_directory
    generate_ca
    generate_server_key_and_csr
    create_server_extensions
    sign_server_certificate
    verify_certificates
    
    if [[ "$quiet" != true ]]; then
        display_certificate_info
    fi
    
    cleanup
    
    log_success "Certificate generation completed successfully!"
    log_info "Certificates are available in the '$CERT_DIR' directory"
    log_info "Files generated:"
    log_info "  - ca.key (CA private key)"
    log_info "  - ca.crt (CA certificate)"
    log_info "  - server.key (Server private key)"
    log_info "  - server.crt (Server certificate)"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
