#!/bin/bash

# Generate a private key
openssl genrsa -out privatekey.pem 4096 ;

# Generate a CSR (Certificate Signing Request)
openssl req -new -key privatekey.pem -out certrequest.csr -subj "/C=US/ST=Virginia/L=Virginia/O=C1/OU=Engineering/CN=tkp.internal"

# Generate a self-signed certificate
openssl x509 -req -days 3650 -in certrequest.csr -signkey privatekey.pem -out certificate.pem

# Generate a certificate chain file
cat certificate.pem >> chain.pem

# Upload the certificate to AWS ACM
aws acm import-certificate --certificate fileb://certificate.pem --private-key fileb://privatekey.pem --certificate-chain fileb://chain.pem --profile default --region us-west-2
