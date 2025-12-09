# DMV Agent MCP - Deployment Reference

**Note:** This is a reference deployment guide. Replace all example values with your actual deployment details.

## Azure Resources

### Function App
- **Name:** `<your-function-app-name>`
- **Resource Group:** `<your-resource-group>`
- **Region:** `<your-region>` (e.g., East US 2)
- **Endpoint:** `https://<your-function-app-name>.azurewebsites.net`
- **Subscription:** `<your-subscription-name>` (`<subscription-id>`)

### Azure SQL Database
- **Server:** `<your-sql-server>.database.windows.net`
- **Database:** `<your-database-name>`
- **User:** `<sql-username>`
- **Password:** `<stored-in-key-vault-or-secure-config>`
- **Table:** `dbo.LicenseAddressChangeRequests` (19 columns)

### MCP Extension System Key
⚠️ **Store securely in Azure Key Vault. Never commit to source control.**

```
<retrieve-from-azure-portal-or-cli>
```

## Connection Strings

### SQL Connection String (Example)
⚠️ **Store in Key Vault or App Settings, never in source control**

```
Driver={ODBC Driver 18 for SQL Server};Server=tcp:<your-server>.database.windows.net,1433;Database=<your-db>;UID=<username>;PWD=<password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
```

## MCP Endpoints

### Local Development
```
http://0.0.0.0:7071/runtime/webhooks/mcp/sse
```

### Production (Azure)
```
https://<your-function-app>.azurewebsites.net/runtime/webhooks/mcp/sse?code=<your-system-key>
```

## Quick Commands

### Get Function App Name from Environment
```bash
FUNCTION_APP_NAME=$(cat .azure/$(cat .azure/config.json | jq -r '.defaultEnvironment')/env.json | jq -r '.FUNCTION_APP_NAME')
echo $FUNCTION_APP_NAME
```

### Get Resource Group
```bash
RESOURCE_GROUP=$(cat .azure/$(cat .azure/config.json | jq -r '.defaultEnvironment')/env.json | jq -r '.AZURE_RESOURCE_GROUP')
echo $RESOURCE_GROUP
```

### View Function Keys
```bash
az functionapp keys list --resource-group $RESOURCE_GROUP --name $FUNCTION_APP_NAME
```

### Update SQL Connection String
```bash
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings SQL_CONNECTION_STRING="<your-connection-string>"
```

### View Function Logs
```bash
az webapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP
```

### Redeploy Code Only
```bash
azd deploy
```

### Full Provision and Deploy
```bash
azd up
```

### Clean Up Resources
```bash
azd down
```

## Testing

### Test with MCP Inspector
1. Start MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector
   ```

2. Connect to production endpoint:
   ```
   https://<your-function-app>.azurewebsites.net/runtime/webhooks/mcp/sse?code=<your-system-key>
   ```

3. List tools and run `create_license_address_change_request`

### Test with curl
```bash
./test-address-change.sh
```

### Verify Data in SQL
```sql
SELECT TOP 10 * FROM dbo.LicenseAddressChangeRequests ORDER BY CreatedAt DESC;
```

## VS Code Copilot Configuration

The `.vscode/mcp.json` file is configured with:
- **Function App Name:** `<your-function-app-name>`
- **MCP Extension Key:** (prompted at runtime)

To use:
1. Command Palette → "List MCP Servers"
2. Start your MCP server
3. Enter key when prompted (retrieve from Azure Portal or CLI)

## MCP Tools Available

### hello_mcp
Simple greeting tool for testing connectivity.

### create_license_address_change_request
Creates Ohio BMV license address change request with 19 parameters:
- driverLicenseNumber, dateOfBirth
- firstName, middleName, lastName
- oldAddressLine1, oldAddressLine2, oldCity, oldState, oldZip
- newAddressLine1, newAddressLine2, newCity, newState, newZip
- phone, email, preferredContactMethod, conversationSummary

## Prerequisites Installed

- Python 3.12.2 (miniconda)
- Azure Functions Core Tools 4.0.7317
- Azure Developer CLI (azd)
- Microsoft ODBC Driver 18 for SQL Server (via Homebrew)
- unixodbc
- pyodbc 5.3.0

## Important Notes

- This is a **proof-of-concept** deployment
- Azure SQL authentication is SQL-based (not Azure AD-only)
- No VNet configured (selected False during deployment)
- Azurite/blob storage not required
- MCP extension uses experimental bundle: Microsoft.Azure.Functions.ExtensionBundle.Experimental [4.*, 5.0.0)

## Troubleshooting

### If function app doesn't connect to SQL
1. Verify connection string is set:
   ```bash
   az functionapp config appsettings list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='SQL_CONNECTION_STRING']"
   ```

2. Check function logs for errors:
   ```bash
   az webapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP
   ```

### If MCP Inspector can't connect
- Verify the system key hasn't changed
- Check that the function app is running (warm it up by visiting the endpoint in a browser)
- Ensure the URL includes the `?code=` parameter

### If SQL INSERT fails
- Verify user has INSERT permissions: `GRANT INSERT ON dbo.LicenseAddressChangeRequests TO <username>;`
- Check that all 19 required parameters are being passed
- Verify date format for dateOfBirth (YYYY-MM-DD)

## Reproduction Steps

To recreate this deployment from scratch:

1. **Install Prerequisites**
   ```bash
   brew install msodbcsql18 unixodbc
   pip install -r src/requirements.txt
   ```

2. **Configure Local Settings**
   - Update `src/local.settings.json` with SQL connection string

3. **Test Locally**
   ```bash
   cd src
   func start
   ```

4. **Deploy to Azure**
   ```bash
   azd up
   ```
   - Select subscription: ME-MngEnvMCAP740785-johncarroll-1
   - Select location: East US 2
   - VNet enabled: False

5. **Configure Azure Function**
   ```bash
   az functionapp config appsettings set \
     --name <function-app-name> \
     --resource-group <resource-group> \
     --settings SQL_CONNECTION_STRING="<connection-string>"
   ```

6. **Get MCP Extension Key**
   ```bash
   az functionapp keys list --resource-group <resource-group> --name <function-app-name>
   ```

7. **Test with MCP Inspector**
   ```bash
   npx @modelcontextprotocol/inspector
   ```
