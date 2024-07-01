#!/bin/bash

# Load environment variables from the .env file
if [ -f .env ]; then
  source .env
fi

# Ensure the required environment variables are set
if [[ -z "$SENTRY_AUTH_TOKEN" || -z "$SENTRY_ORG" || -z "$SENTRY_PROJECT" ]]; then
  echo "Please set the SENTRY_AUTH_TOKEN, SENTRY_ORG, and SENTRY_PROJECT environment variables."
  exit 1
fi

# Define the release version (you can automate this based on your versioning system)
RELEASE_VERSION="chatbot-server@1.0.0"

# Create a new release
sentry-cli releases new $RELEASE_VERSION

# Associate commits automatically
sentry-cli releases set-commits --auto $RELEASE_VERSION

# Finalize the release
sentry-cli releases finalize $RELEASE_VERSION

# Notify Sentry of a new deploy
sentry-cli releases deploys $RELEASE_VERSION new -e production

echo "Sentry release process completed for version $RELEASE_VERSION"