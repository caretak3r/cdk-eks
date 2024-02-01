#!/bin/bash

DOMAIN=$1
if [ -z "$1" ]; then 

    echo "USAGE: $0 domain.lan"
    echo ""
    echo "This will generate a non-secure self-signed wildcard certificate for given domain."
    echo "This should only be used in a development environment."
    exit
fi

# Add wildcard
WILDCARD="*.$DOMAIN"

# Set our CSR variables
SUBJ="
C=US
ST=VA
O=C1
localityName=LocalDevelopement
commonName=$WILDCARD
organizationalUnitName=Engineering
"

# Generate a private key
openssl genrsa -out "$DOMAIN.pem" 4096 ;

# Generate a CSR (Certificate Signing Request)
#openssl req -new -key "$DOMAIN.pem" -out "$DOMAIN.csr" -subj "/C=US/ST=Virginia/L=Virginia/O=C1/OU=Engineering/CN=tkp.internal"
openssl req -new -key "$DOMAIN.pem" -out "$DOMAIN.csr" -subj "$(echo -n "$SUBJ" | tr "\n" "/")" ;

# Generate a self-signed certificate
openssl x509 -req -days 3650 -in "$DOMAIN.csr" -signkey "$DOMAIN.pem" -out "$DOMAIN-cert.pem" ;

# Generate a certificate chain file
cat "$DOMAIN-cert.pem" >> "$DOMAIN-fullchain.pem" ;

# Upload the certificate to AWS ACM
aws acm import-certificate --certificate fileb://"$DOMAIN-cert.pem" --private-key fileb://"$DOMAIN.pem" --certificate-chain fileb://"$DOMAIN-fullchain.pem" --profile default --region us-west-2
