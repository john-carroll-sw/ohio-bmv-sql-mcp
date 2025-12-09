import os
import json
import logging

import pyodbc
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


class ToolProperty:
    def __init__(self, property_name: str, property_type: str, description: str):
        self.propertyName = property_name
        self.propertyType = property_type
        self.description = description

    def to_dict(self):
        return {
            "propertyName": self.propertyName,
            "propertyType": self.propertyType,
            "description": self.description,
        }


# Define the tool properties for license address change
tool_properties_license_address_change_object = [
    ToolProperty("driverLicenseNumber", "string", "Ohio driver's license number for the customer (required)."),
    ToolProperty("dateOfBirth", "string", "Customer date of birth in YYYY-MM-DD format (required)."),
    ToolProperty("firstName", "string", "Customer first name (required)."),
    ToolProperty("middleName", "string", "Customer middle name (optional)."),
    ToolProperty("lastName", "string", "Customer last name (required)."),
    ToolProperty("email", "string", "Customer email address (optional)."),
    ToolProperty("phone", "string", "Customer phone number (optional)."),
    ToolProperty("oldAddressLine1", "string", "Previous street address line 1 (required)."),
    ToolProperty("oldAddressLine2", "string", "Previous street address line 2 (optional)."),
    ToolProperty("oldCity", "string", "Previous city (required)."),
    ToolProperty("oldState", "string", "Previous state two-letter code (required, e.g. 'OH')."),
    ToolProperty("oldZip", "string", "Previous ZIP or ZIP+4 (required)."),
    ToolProperty("newAddressLine1", "string", "New street address line 1 (required)."),
    ToolProperty("newAddressLine2", "string", "New street address line 2 (optional)."),
    ToolProperty("newCity", "string", "New city (required)."),
    ToolProperty("newState", "string", "New state two-letter code (required, e.g. 'OH')."),
    ToolProperty("newZip", "string", "New ZIP or ZIP+4 (required)."),
    ToolProperty("preferredContactMethod", "string", "How the customer prefers to be contacted: 'email', 'phone', or 'mail'."),
    ToolProperty("conversationSummary", "string", "Short summary of the chat about this address change, for audit purposes."),
]

tool_properties_license_address_change_json = json.dumps(
    [prop.to_dict() for prop in tool_properties_license_address_change_object]
)

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="hello_mcp",
    description="Hello world.",
    toolProperties="[]",
)
def hello_mcp(context) -> None:
    """
    A simple function that returns a greeting message.

    Args:
        context: The trigger context (not used in this function).

    Returns:
        str: A greeting message.
    """
    return "Hello I am MCPTool!"


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="create_license_address_change_request",
    description="Create an Ohio BMV driver's license address-change request record in SQL.",
    toolProperties=tool_properties_license_address_change_json,
)
def create_license_address_change_request(context) -> str:
    """
    Inserts a driver's license address-change request into the
    LicenseAddressChangeRequests table in Azure SQL.
    """
    try:
        content = json.loads(context)
        args = content.get("arguments", {})

        # Pull arguments out of the MCP payload
        dln =       args.get("driverLicenseNumber")
        dob =       args.get("dateOfBirth")
        first =     args.get("firstName")
        middle =    args.get("middleName")
        last =      args.get("lastName")
        
        email =     args.get("email")
        phone =     args.get("phone")
        old1 =      args.get("oldAddressLine1")
        old2 =      args.get("oldAddressLine2")
        old_city =  args.get("oldCity")
        
        old_state = args.get("oldState")
        old_zip =   args.get("oldZip")
        new1 =      args.get("newAddressLine1")
        new2 =      args.get("newAddressLine2")
        new_city =  args.get("newCity")
        
        new_state = args.get("newState")
        new_zip =   args.get("newZip")
        contact =   args.get("preferredContactMethod")
        summary =   args.get("conversationSummary")

        # Basic required-field check
        required = {
            "driverLicenseNumber": dln,
            "dateOfBirth": dob,
            "firstName": first,
            "lastName": last,
            "oldAddressLine1": old1,
            "oldCity": old_city,
            "oldState": old_state,
            "oldZip": old_zip,
            "newAddressLine1": new1,
            "newCity": new_city,
            "newState": new_state,
            "newZip": new_zip,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"

        conn_str = os.environ.get("SQL_CONNECTION_STRING")
        if not conn_str:
            return "SQL_CONNECTION_STRING environment variable is not set."

        logging.info(f"Attempting SQL connection to database for DLN={dln}")
        try:
            conn = pyodbc.connect(conn_str)
            logging.info("SQL connection established successfully")
        except Exception as conn_error:
            logging.error(f"Failed to connect to database: {conn_error}")
            return f"Database connection failed: {conn_error}"
        
        cursor = conn.cursor()

        logging.info(f"Executing INSERT for DLN={dln}, Name={first} {last}")
        try:
            cursor.execute(
                """
                INSERT INTO LicenseAddressChangeRequests (
                    DriverLicenseNumber,
                    DateOfBirth,
                    FirstName,
                    MiddleName,
                    LastName,
                    Email,
                    Phone,
                    OldAddressLine1,
                    OldAddressLine2,
                    OldCity,
                    OldState,
                    OldZip,
                    NewAddressLine1,
                    NewAddressLine2,
                    NewCity,
                    NewState,
                    NewZip,
                    PreferredContactMethod,
                    ConversationSummary
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (dln,
                dob,
                first,
                middle,
                last,
                email,
                phone,
                old1,
                old2,
                old_city,
                old_state,
                old_zip,
                new1,
                new2,
                new_city,
                new_state,
                new_zip,
                contact,
                summary)
            )

            conn.commit()
            logging.info("INSERT committed successfully")

            # Get the identity of the inserted row
            cursor.execute("SELECT SCOPE_IDENTITY()")
            row_id_result = cursor.fetchone()
            row_id = row_id_result[0] if row_id_result and row_id_result[0] is not None else None

            if row_id:
                logging.info(f"Created LicenseAddressChangeRequests.Id={row_id} for DLN={dln}")
                return f"Created address-change request #{int(row_id)} for license {dln}."
            else:
                logging.info(f"Created LicenseAddressChangeRequests for DLN={dln} (ID not available)")
                return f"Successfully created address-change request for license {dln}."
        except Exception as insert_error:
            logging.error(f"Failed to execute INSERT: {insert_error}")
            conn.rollback()
            return f"Database INSERT failed: {insert_error}"
        finally:
            cursor.close()
            conn.close()
            logging.info("Database connection closed")

    except Exception as e:
        logging.exception("Error inserting license address-change request")
        return f"Failed to create address-change request: {e}"
