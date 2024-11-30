SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(cat "$SCRIPT_DIR/../.env" | grep -v '#' | awk '/=/ {print $1}')
else
    echo "The .env file does not exist."
    exit 1
fi

# Prepare the JWT
HEADER=$(echo -n '{"alg":"RS256","typ":"JWT"}' | base64 -w 0 | tr '+/' '-_' | tr -d '=')
CLAIMS=$(echo -n '{
  "iss": "'$(jq -r .client_email < $SERVICE_ACCOUNT_KEY)'",
  "scope": "https://www.googleapis.com/auth/drive.file",
  "aud": "'$TOKEN_URL'",
  "exp": '$(($(date +%s)+3600))',
  "iat": '$(date +%s)'
}' | base64 -w 0 | tr '+/' '-_' | tr -d '=')
SIGNATURE=$(echo -n "${HEADER}.${CLAIMS}" | openssl dgst -sha256 -sign <(jq -r .private_key < $SERVICE_ACCOUNT_KEY) | base64 -w 0 | tr '+/' '-_' | tr -d '=')

# Combine all parts to form the signed JWT
JWT="${HEADER}.${CLAIMS}.${SIGNATURE}"

# Get the OAuth 2.0 token
ACCESS_TOKEN=$(curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
  -d "assertion=${JWT}" \
  ${TOKEN_URL} | jq -r .access_token)

echo "The token has been put in $ACCESS_TOKEN_FILE"
echo "$ACCESS_TOKEN" > $ACCESS_TOKEN_FILE


