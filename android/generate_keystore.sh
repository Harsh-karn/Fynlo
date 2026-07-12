#!/bin/bash
# Script to generate a secure release keystore for Google Play Store Android app bundles

KEYSTORE_NAME="app/release.keystore"
ALIAS="fynlo-key"

echo "Generating Google Play Release Keystore for Fynlo..."
echo "WARNING: Do NOT lose this file or the password you are about to set."
echo "If you lose it, you will not be able to update your app on the Play Store."
echo ""

keytool -genkeypair -v \
  -storetype PKCS12 \
  -keystore $KEYSTORE_NAME \
  -alias $ALIAS \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

echo ""
echo "✅ Keystore generated at: android/$KEYSTORE_NAME"
echo "Next step: Run './gradlew bundleRelease' to generate your .aab file!"
