<!--
---
name: Ohio BMV License Address Change - MCP Server (Python)
description: MCP server for Ohio Bureau of Motor Vehicles license address change requests using Azure Functions and Azure SQL.
page_type: sample
languages:
- python
- bicep
- azdeveloper
products:
- azure-functions
- azure-sql
- azure
urlFragment: ohio-bmv-sql-mcp
---
-->

# Ohio BMV License Address Change - MCP Server

This is an MCP (Model Context Protocol) server that enables AI assistants to capture and process Ohio driver's license address change requests. Built with Azure Functions (Python) and Azure SQL Database, it demonstrates how conversational AI can interact with structured database systems to handle government service requests.

## Business Context

This proof-of-concept enables an AI assistant (ChatGPT, GitHub Copilot, or custom agent) to:

- Collect required information through natural conversation
- Validate address change data
- Persist requests directly to Azure SQL Database
- Provide confirmation to the user

**Use Case:** A citizen tells an AI assistant they've moved, and the assistant guides them through updating their driver's license address by calling this MCP tool to store the information in the BMV's system.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/remote-mcp-functions-python)

Below is the architecture diagram for the Remote MCP Server using Azure Functions:

![Architecture Diagram](architecture-diagram.png)

## Prerequisites

- [Python](https://www.python.org/downloads/) version 3.11 or higher
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local?pivots=programming-language-python#install-the-azure-functions-core-tools) >= `4.0.7030`
- [Azure Developer CLI](https://aka.ms/azd)
- To use Visual Studio Code to run and debug locally:
  - [Visual Studio Code](https://code.visualstudio.com/)
  - [Azure Functions extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)

### Additional Prerequisites for SQL Database Integration

This project connects to Azure SQL Database using ODBC. You'll need to install the Microsoft ODBC Driver for SQL Server:

**macOS:**

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql18 unixodbc
```

**Linux (Ubuntu/Debian):**

```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```

**Windows:**

Download and install from [Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Prepare your local environment

Unlike the base template, this project **does not require Azurite** (Azure Storage Emulator) as it only uses Azure SQL Database for data persistence.

## Run your MCP Server locally from the terminal

1. Change to the src folder in a new terminal window:

   ```shell
   cd src
   ```

1. Install Python dependencies:

   ```shell
   pip install -r requirements.txt
   ```

>**Note** it is a best practice to create a Virtual Environment before doing the `pip install` to avoid dependency issues/collisions, or if you are running in CodeSpaces.  See [Python Environments in VS Code](https://code.visualstudio.com/docs/python/environments#_creating-environments) for more information.

1. Start the Functions host locally:

   ```shell
   func start
   ```

> **Note** by default this will use the webhooks route: `/runtime/webhooks/mcp/sse`.  Later we will use this in Azure to set the key on client/host calls: `/runtime/webhooks/mcp/sse?code=<system_key>`

## Connect to the *local* MCP server from a client/host

### VS Code - Copilot agent mode

1. **Add MCP Server** from command palette and add URL to your running Function app's SSE endpoint:

    ```shell
    http://0.0.0.0:7071/runtime/webhooks/mcp/sse
    ```

1. **List MCP Servers** from command palette and start the server

1. In Copilot chat agent mode enter a prompt to trigger the tool:

    ```plaintext
    I moved from 123 Old Street, Columbus, OH 43215 to 456 New Avenue, Dayton, OH 45402. 
    Please update my Ohio driver's license address. My license number is OH12345678 and 
    my date of birth is June 15, 1985.
    ```

1. When prompted to run the tool, consent by clicking **Continue**

1. When you're done, press Ctrl+C in the terminal window to stop the Functions host process.

### MCP Inspector

1. In a **new terminal window**, install and run MCP Inspector

    ```shell
    npx @modelcontextprotocol/inspector
    ```

1. Open the MCP Inspector web app from the URL displayed (e.g., <http://0.0.0.0:5173>)

1. Set the transport type to `SSE`

1. Set the URL to your running Function app's SSE endpoint and **Connect**:

    ```shell
    http://0.0.0.0:7071/runtime/webhooks/mcp/sse
    ```

    >**Note** this step will not work in CodeSpaces. Please move on to Deploy to Remote MCP.

1. **List Tools**. Click on `create_license_address_change_request` and **Run Tool** with test data.

## Verify the Data in Azure SQL

After successfully running the tool, you can verify that the address change request was stored:

1. Log into the Azure Portal (<https://portal.azure.com>)
1. Navigate to your Azure SQL Database (ohio-bmv-demo-db)
1. Go to **Query editor** (or use SQL Server Management Studio)
1. Run the following query:

   ```sql
   SELECT TOP 10 * FROM dbo.LicenseAddressChangeRequests ORDER BY CreatedAt DESC;
   ```

1. Verify that your test data appears in the results

## Deploy to Azure for Remote MCP

Run this [azd](https://aka.ms/azd) command to provision the function app, with any required Azure resources, and deploy your code:

```shell
azd up
```

You can opt-in to a VNet being used in the sample. To do so, do this before `azd up`

```bash
azd env set VNET_ENABLED true
```

Additionally, [API Management] can be used for improved security and policies over your MCP Server, and [App Service built-in authentication](https://learn.microsoft.com/azure/app-service/overview-authentication-authorization) can be used to set up your favorite OAuth provider including Entra.  

## Connect to your *remote* MCP server function app from a client

Your client will need a key in order to invoke the new hosted SSE endpoint, which will be of the form `https://<funcappname>.azurewebsites.net/runtime/webhooks/mcp/sse`. The hosted function requires a system key by default which can be obtained from the [portal](https://learn.microsoft.com/azure/azure-functions/function-keys-how-to?tabs=azure-portal) or the CLI (`az functionapp keys list --resource-group <resource_group> --name <function_app_name>`). Obtain the system key named `mcp_extension`.

### Connect to remote MCP server in MCP Inspector

For MCP Inspector, you can include the key in the URL:

```plaintext
https://<funcappname>.azurewebsites.net/runtime/webhooks/mcp/sse?code=<your-mcp-extension-system-key>
```

### Connect to remote MCP server in VS Code - GitHub Copilot

For GitHub Copilot within VS Code, you should instead set the key as the `x-functions-key` header in `mcp.json`, and you would just use `https://<funcappname>.azurewebsites.net/runtime/webhooks/mcp/sse` for the URL. The following example uses an input and will prompt you to provide the key when you start the server from VS Code.  Note [mcp.json](.vscode/mcp.json) has already been included in this repo and will be picked up by VS Code.  Click Start on the server to be prompted for values including `functionapp-name` (in your /.azure/*/.env file) and `functions-mcp-extension-system-key` which can be obtained from CLI command above or API Keys in the portal for the Function App.  

```json
{
    "inputs": [
        {
            "type": "promptString",
            "id": "functions-mcp-extension-system-key",
            "description": "Azure Functions MCP Extension System Key",
            "password": true
        },
        {
            "type": "promptString",
            "id": "functionapp-name",
            "description": "Azure Functions App Name"
        }
    ],
    "servers": {
        "remote-mcp-function": {
            "type": "sse",
            "url": "https://${input:functionapp-name}.azurewebsites.net/runtime/webhooks/mcp/sse",
            "headers": {
                "x-functions-key": "${input:functions-mcp-extension-system-key}"
            }
        },
        "local-mcp-function": {
            "type": "sse",
            "url": "http://0.0.0.0:7071/runtime/webhooks/mcp/sse"
        }
    }
}
```

For MCP Inspector, you can include the key in the URL: `https://<funcappname>.azurewebsites.net/runtime/webhooks/mcp/sse?code=<your-mcp-extension-system-key>`.

For GitHub Copilot within VS Code, you should instead set the key as the `x-functions-key` header in `mcp.json`, and you would just use `https://<funcappname>.azurewebsites.net/runtime/webhooks/mcp/sse` for the URL. The following example uses an input and will prompt you to provide the key when you start the server from VS Code:

```json
{
    "inputs": [
        {
            "type": "promptString",
            "id": "functions-mcp-extension-system-key",
            "description": "Azure Functions MCP Extension System Key",
            "password": true
        }
    ],
    "servers": {
        "my-mcp-server": {
            "type": "sse",
            "url": "<funcappname>.azurewebsites.net/runtime/webhooks/mcp/sse",
            "headers": {
                "x-functions-key": "${input:functions-mcp-extension-system-key}"
            }
        }
    }
}
```

## Redeploy your code

You can run the `azd up` command as many times as you need to both provision your Azure resources and deploy code updates to your function app.

>[!NOTE]
>Deployed code files are always overwritten by the latest deployment package.

## Clean up resources

When you're done working with your function app and related resources, you can use this command to delete the function app and its related resources from Azure and avoid incurring any further costs:

```shell
azd down
```

## Helpful Azure Commands

Once your application is deployed, you can use these commands to manage and monitor your application:

```bash
# Get your function app name from the environment file
FUNCTION_APP_NAME=$(cat .azure/$(cat .azure/config.json | jq -r '.defaultEnvironment')/env.json | jq -r '.FUNCTION_APP_NAME')
echo $FUNCTION_APP_NAME

# Get resource group 
RESOURCE_GROUP=$(cat .azure/$(cat .azure/config.json | jq -r '.defaultEnvironment')/env.json | jq -r '.AZURE_RESOURCE_GROUP')
echo $RESOURCE_GROUP

# View function app logs
az webapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Redeploy the application without provisioning new resources
azd deploy
```

## Source Code

The function code for the license address change endpoint is defined in `src/function_app.py`. The MCP function annotation exposes this function as an MCP Server tool that can be called conversationally by AI agents.

Here's the main function from function_app.py:

```python
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="create_license_address_change_request",
    description="Create an Ohio BMV driver's license address-change request record in SQL.",
    toolProperties=tool_properties_create_license_json
)
def create_license_address_change_request(context) -> str:
    """
    Creates an address change request for an Ohio driver's license in Azure SQL.
    
    Args:
        context: The trigger context containing all address change parameters.
        
    Returns:
        str: A success message with the driver license number or an error message.
    """
    try:
        # Parse the context to extract address change parameters
        dln = context.get("driverLicenseNumber")
        dob = context.get("dateOfBirth")
        first = context.get("firstName")
        middle = context.get("middleName")
        last = context.get("lastName")
        
        old_addr1 = context.get("oldAddressLine1")
        old_addr2 = context.get("oldAddressLine2")
        old_city = context.get("oldCity")
        old_state = context.get("oldState")
        old_zip = context.get("oldZip")
        
        new_addr1 = context.get("newAddressLine1")
        new_addr2 = context.get("newAddressLine2")
        new_city = context.get("newCity")
        new_state = context.get("newState")
        new_zip = context.get("newZip")
        
        phone = context.get("phone")
        email = context.get("email")
        preferred_contact = context.get("preferredContactMethod")
        conversation_summary = context.get("conversationSummary")
        
        # Validate required fields
        if not all([dln, dob, first, last, old_addr1, old_city, old_state, 
                   old_zip, new_addr1, new_city, new_state, new_zip]):
            return "Error: Missing required fields for address change request."
        
        # Get database connection string
        connection_string = os.environ["SQL_CONNECTION_STRING"]
        
        # Connect and insert
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO dbo.LicenseAddressChangeRequests 
        (DriverLicenseNumber, DateOfBirth, FirstName, MiddleName, LastName,
         OldAddressLine1, OldAddressLine2, OldCity, OldState, OldZip,
         NewAddressLine1, NewAddressLine2, NewCity, NewState, NewZip,
         Phone, Email, PreferredContactMethod, ConversationSummary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        SELECT SCOPE_IDENTITY();
        """
        
        cursor.execute(insert_sql, (
            dln, dob, first, middle, last,
            old_addr1, old_addr2, old_city, old_state, old_zip,
            new_addr1, new_addr2, new_city, new_state, new_zip,
            phone, email, preferred_contact, conversation_summary
        ))
        
        result = cursor.fetchone()
        request_id = result[0] if result and result[0] else None
        
        conn.commit()
        cursor.close()
        conn.close()
        
        if request_id:
            return f"Successfully created address-change request (ID: {request_id}) for license {dln}."
        else:
            return f"Successfully created address-change request for license {dln}."
            
    except Exception as e:
        logging.error(f"Error creating address change request: {str(e)}")
        return f"Error: {str(e)}"
```

Note that the `host.json` file also includes a reference to the experimental bundle, which is required for apps using this feature:

```json
"extensionBundle": {
  "id": "Microsoft.Azure.Functions.ExtensionBundle.Experimental",
  "version": "[4.*, 5.0.0)"
}
```

## Next Steps

- Add [API Management](https://aka.ms/mcp-remote-apim-auth) to your MCP server (auth, gateway, policies, more!)
- Add [built-in auth](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization) to your MCP server
- Enable VNET using VNET_ENABLED=true flag
- Learn more about [related MCP efforts from Microsoft](https://github.com/microsoft/mcp/tree/main/Resources)
