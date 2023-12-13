#!/bin/bash

# Check if AWS SSO credentials are present
for file in ~/.aws/sso/cache/*; do
    if [ -f "$file" ]; then
        # Get the SSO session token details
        SESSION_TOKEN=$(aws sso get-role-credentials --profile your-profile-name)
        break
    fi
done
if [ -z "$SESSION_TOKEN" ]; then
    # Get the session token details
    SESSION_TOKEN=$(aws sts get-session-token)
fi

# Extract the expiration time
EXPIRATION=$(echo "$SESSION_TOKEN" | jq -r '.Credentials.Expiration')

# Convert the expiration time to Unix timestamp
EXPIRATION_TIMESTAMP=$(date -d"$EXPIRATION" +%s)

# Get the current time in Unix timestamp
CURRENT_TIMESTAMP=$(date +%s)

# Calculate the difference in minutes
DIFFERENCE_MINUTES=$(( ($EXPIRATION_TIMESTAMP - $CURRENT_TIMESTAMP) / 60 ))

# Check if the session will expire in less than 5 minutes
if [ $DIFFERENCE_MINUTES -lt 5 ]; then
    echo "Your AWS session will expire in less than 5 minutes. Refreshing credentials..."
    # Refresh the credentials
    for file in ~/.aws/sso/cache/*; do
        if [ -f "$file" ]; then
            # Refresh the SSO credentials
            aws sso login --profile your-profile-name
            break
        fi
    done
    if [ -z "$file" ]; then
        # Refresh the STS credentials
        aws sts get-session-token
    fi
        aws sts get-session-token
    fi
else
    echo "Your AWS session is valid for more than 5 minutes."
fi
