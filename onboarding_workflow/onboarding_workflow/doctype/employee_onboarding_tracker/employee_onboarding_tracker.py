# Copyright (c) 2025, Muhammad Shahzad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class EmployeeOnboardingTracker(Document):
    def validate(self):
        if self.status == "Completed":
            incomplete = [row.task for row in self.checklist if not row.is_completed]
            if incomplete:
                frappe.throw(f"Tracker cannot be marked as Completed. These tasks are still pending: {', '.join(incomplete)}")

        required_asset = self.required_asset or []

        for asset in required_asset:
            if not asset.asset_name or not asset.quantity:
                continue

            schedule_date = asset.needed_by
            if not schedule_date:
                schedule_date = nowdate()  
            elif getdate(schedule_date) < getdate(nowdate()):
                schedule_date = nowdate()  
            actual_qty = frappe.db.get_value("Bin", {"item_code": asset.asset_name}, "actual_qty") or 0
            if actual_qty < asset.quantity:
                try:
                    mr = frappe.get_doc({
                        "doctype": "Material Request",
                        "material_request_type": "Purchase",
                        "transaction_date": nowdate(),  
                        "schedule_date": schedule_date,  
                        "items": [
                            {
                                "item_code": asset.asset_name,
                                "qty": asset.quantity,
                                "schedule_date": schedule_date
                            }
                        ]
                    })
                    mr.insert(ignore_permissions=True)
                    mr.submit()
                except Exception as e:
                    frappe.log_error(f"Failed to create Material Request for asset {asset.asset_name}: {str(e)}", "EmployeeOnboardingTracker")
                    frappe.msgprint(f"Error creating Material Request for {asset.asset_name}: {str(e)}")