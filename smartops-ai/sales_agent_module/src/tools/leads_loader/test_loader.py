from .lead_loader_base import LeadLoaderBase

class TestLeadLoader(LeadLoaderBase):
    """
    Built-in local loader providing 3 realistic demo prospects for offline testing:
    1. Strong fit (Good fit)
    2. Maybe fit (Maybe)
    3. Poor fit (Not a fit right now - exercises unqualified branch)
    """
    def __init__(self):
        self.leads = [
            {
                "id": "prospect_001",
                "Name": "Alex Mercer",
                "First Name": "Alex",
                "Last Name": "Mercer",
                "Company": "Apex Dynamics",
                "Email": "alex.mercer@example.com",
                "Website": "https://apexdynamics.example.com",
                "Role": "VP of Operations",
                "Note": "Growing mid-market B2B distributor experiencing customer support delays and high ticket volume.",
                "Phone": "+1-555-0192",
                "Address": "Austin, TX",
                "Status": "NEW"
            },
            {
                "id": "prospect_002",
                "Name": "Elena Rostova",
                "First Name": "Elena",
                "Last Name": "Rostova",
                "Company": "FinTech Cloud Solutions",
                "Email": "elena.rostova@example.com",
                "Website": "https://fintechcloud.example.com",
                "Role": "Chief Customer Officer",
                "Note": "Evaluating automation solutions, but currently transitioning core ticketing platforms.",
                "Phone": "+1-555-0144",
                "Address": "Chicago, IL",
                "Status": "NEW"
            },
            {
                "id": "prospect_003",
                "Name": "Timmy Small",
                "First Name": "Timmy",
                "Last Name": "Small",
                "Company": "Timmy's Solo Hobby Blog",
                "Email": "timmy@example.com",
                "Website": "https://timmyblog.example.com",
                "Role": "Solo Blogger",
                "Note": "Individual content creator with zero B2B operations or support staff.",
                "Phone": "+1-555-0188",
                "Address": "Portland, OR",
                "Status": "NEW"
            }
        ]

    def fetch_records(self, status_filter=None):
        if status_filter:
            return [l for l in self.leads if l.get("Status") == status_filter]
        return self.leads

    def add_lead(self, name, company, email, website=None, note="Custom added prospect"):
        new_id = f"custom_{len(self.leads)+1}"
        parts = name.split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""
        lead = {
            "id": new_id,
            "Name": name,
            "First Name": first,
            "Last Name": last,
            "Company": company,
            "Email": email,
            "Website": website or f"https://{company.lower().replace(' ', '')}.example.com",
            "Role": "Prospect Contact",
            "Note": note,
            "Status": "NEW"
        }
        self.leads.append(lead)
        return lead

    def update_record(self, lead_id, updates):
        for l in self.leads:
            if l["id"] == lead_id:
                if isinstance(updates, dict):
                    l.update(updates)
                else:
                    l["Status"] = updates
                return l
        return None
