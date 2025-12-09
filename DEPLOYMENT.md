# Ohio BMV SQL MCP - Deployment Reference

**Created:** December 2, 2025  
**Environment:** ohio-bmv-sql-mcp

## Azure Resources

### Function App
- **Name:** `func-api-lwtfpn4ptwceg`
- **Resource Group:** `rg-ohio-bmv-sql-mcp`
- **Region:** East US 2 (eastus2)
- **Endpoint:** https://func-api-lwtfpn4ptwceg.azurewebsites.net
- **Subscription:** ME-MngEnvMCAP740785-johncarroll-1 (e7b12c0e-51b7-4507-af01-6ea306d0b194)

### Azure SQL Database
- **Server:** ohio-bmv-demo-sql.database.windows.net
- **Database:** ohio-bmv-demo-db
- **User:** bmv_bot
- **Password:** SuperStrongP@ssword123!
- **Table:** dbo.LicenseAddressChangeRequests (19 columns)

### MCP Extension System Key
```
-5fiL9J8le5mT_yMurHSdMB3M_wO99b5A90V4nO7BU3BAzFuM4X_HA==
```

## Connection Strings

### SQL Connection String
```
Driver={ODBC Driver 18 for SQL Server};Server=tcp:ohio-bmv-demo-sql.database.windows.net,1433;Database=ohio-bmv-demo-db;UID=bmv_bot;PWD=SuperStrongP@ssword123!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
```

## MCP Endpoints

### Local Development
```
http://0.0.0.0:7071/runtime/webhooks/mcp/sse
```

### Production (Azure)
```
https://func-api-lwtfpn4ptwceg.azurewebsites.net/runtime/webhooks/mcp/sse?code=-5fiL9J8le5mT_yMurHSdMB3M_wO99b5A90V4nO7BU3BAzFuM4X_HA==
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
az functionapp keys list --resource-group rg-ohio-bmv-sql-mcp --name func-api-lwtfpn4ptwceg
```

### Update SQL Connection String
```bash
az functionapp config appsettings set \
  --name func-api-lwtfpn4ptwceg \
  --resource-group rg-ohio-bmv-sql-mcp \
  --settings SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:ohio-bmv-demo-sql.database.windows.net,1433;Database=ohio-bmv-demo-db;UID=bmv_bot;PWD=SuperStrongP@ssword123!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

### View Function Logs
```bash
az webapp log tail --name func-api-lwtfpn4ptwceg --resource-group rg-ohio-bmv-sql-mcp
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
   https://func-api-lwtfpn4ptwceg.azurewebsites.net/runtime/webhooks/mcp/sse?code=-5fiL9J8le5mT_yMurHSdMB3M_wO99b5A90V4nO7BU3BAzFuM4X_HA==
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
- **Function App Name:** func-api-lwtfpn4ptwceg
- **MCP Extension Key:** (prompted at runtime)

To use:
1. Command Palette → "List MCP Servers"
2. Start "remote-mcp-function"
3. Enter key when prompted: `-5fiL9J8le5mT_yMurHSdMB3M_wO99b5A90V4nO7BU3BAzFuM4X_HA==`

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
   az functionapp config appsettings list --name func-api-lwtfpn4ptwceg --resource-group rg-ohio-bmv-sql-mcp --query "[?name=='SQL_CONNECTION_STRING']"
   ```

2. Check function logs for errors:
   ```bash
   az webapp log tail --name func-api-lwtfpn4ptwceg --resource-group rg-ohio-bmv-sql-mcp
   ```

### If MCP Inspector can't connect
- Verify the system key hasn't changed
- Check that the function app is running (warm it up by visiting the endpoint in a browser)
- Ensure the URL includes the `?code=` parameter

### If SQL INSERT fails
- Verify bmv_bot user has INSERT permissions: `GRANT INSERT ON dbo.LicenseAddressChangeRequests TO bmv_bot;`
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
