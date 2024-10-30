# solanaTxnWebhook

Flask app to listen for Solana transaction webhooks and save raw JSON to MongoDB.

## Setup

### Required Environment Variables

- `MONGO_HOST`: MongoDB host
- `MONGO_PORT`: MongoDB port
- `MONGO_USER`: MongoDB username
- `MONGO_PWD`: MongoDB password
- `MONGO_DB`: MongoDB database name (MONGO_USER should authenticate to this DB and have read/write access)
- `MONGO_COLLECTION`: MongoDB collection name

### Optional Environment Variable:

- `MONGO_TLS`: MongoDB TLS required (True/False)

### MongoDB Schema

- **_id:** $SOL txn id
- **timestamp:** $SOL txn blocktime
- **txn:** $SOL txn raw JSON