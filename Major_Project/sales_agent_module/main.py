import os
from dotenv import load_dotenv
from src.graph import OutReachAutomation
from src.state import *
from src.tools.leads_loader.airtable import AirtableLeadLoader
from src.tools.leads_loader.google_sheets import GoogleSheetLeadLoader

# Load environment variables from a .env file
load_dotenv()

from src.tools.leads_loader.test_loader import TestLeadLoader
import sys

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    airtable_token = os.getenv("AIRTABLE_ACCESS_TOKEN")
    airtable_base = os.getenv("AIRTABLE_BASE_ID")
    
    if airtable_token and airtable_base:
        print("🔗 Connecting to Airtable CRM...")
        lead_loader = AirtableLeadLoader(
            access_token=airtable_token,
            base_id=airtable_base,
            table_name=os.getenv("AIRTABLE_TABLE_NAME", "Leads"),
        )
    else:
        print("ℹ️ No Airtable credentials detected in .env. Using built-in test lead (Microsoft / John Doe)...")
        lead_loader = TestLeadLoader()
    
    # Instantiate the OutReachAutomation class
    automation = OutReachAutomation(lead_loader)
    app = automation.app
    
    # initial graph inputs:
    # Lead ids to be processed, leave empty to fetch all news leads
    inputs = {"leads_ids": []}


    # Run the outreach automation with the provided lead name and email
    config = {'recursion_limit': 1000}
    output = app.invoke(inputs, config)
    print(output)