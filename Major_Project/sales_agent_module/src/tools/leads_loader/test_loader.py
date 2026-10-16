from .lead_loader_base import LeadLoaderBase

class TestLeadLoader(LeadLoaderBase):
    """
    Built-in local loader providing test leads for offline or demo testing
    without requiring external CRM credentials.
    """
    def __init__(self):
        self.leads = [
            {
                "id": "lead_test_001",
                "Name": "John Doe",
                "First Name": "John",
                "Last Name": "Doe",
                "Company": "Microsoft",
                "Email": "satya@microsoft.com",
                "LinkedIn Profile": "https://www.linkedin.com/in/satyanadella/",
                "Phone": "+1-425-882-8080",
                "Address": "Redmond, WA",
                "Status": "NEW"
            }
        ]

    def fetch_records(self, status_filter="NEW"):
        return [l for l in self.leads if l.get("Status") == status_filter]

    def update_record(self, lead_id, updates):
        for l in self.leads:
            if l["id"] == lead_id:
                if isinstance(updates, dict):
                    l.update(updates)
                else:
                    l["Status"] = updates
                return l
        return None
