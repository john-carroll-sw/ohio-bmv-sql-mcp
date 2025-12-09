#!/bin/bash

# Test script for create_license_address_change_request MCP tool
# This sends a JSON-RPC tools/call request to the local Azure Functions MCP endpoint

curl -X POST http://localhost:7071/runtime/webhooks/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "create_license_address_change_request",
      "arguments": {
        "driverLicenseNumber": "OH12345678",
        "dateOfBirth": "1985-06-15",
        "firstName": "Jane",
        "middleName": "Marie",
        "lastName": "Smith",
        "email": "jane.smith@example.com",
        "phone": "614-555-1234",
        "oldAddressLine1": "123 Old Street",
        "oldAddressLine2": "Apt 4B",
        "oldCity": "Columbus",
        "oldState": "OH",
        "oldZip": "43215",
        "newAddressLine1": "456 New Avenue",
        "newAddressLine2": "",
        "newCity": "Dayton",
        "newState": "OH",
        "newZip": "45402",
        "preferredContactMethod": "email",
        "conversationSummary": "Customer moved from Columbus to Dayton. Updated address for driver license renewal."
      }
    }
  }'
