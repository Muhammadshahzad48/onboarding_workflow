// Copyright (c) 2025, Muhammad Shahzad and contributors
// For license information, please see license.txt

frappe.query_reports["Pending Onboarding Tasks"] = {
	"filters": [
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nAssigned\nIn Progress"
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname === "status") {
            if (value === "In Progress") {
                value = `<span style="color: orange;">${value}</span>`;
            } else if (value === "Draft") {
                value = `<span style="color: red;">${value}</span>`;
            }
        }
        
        if (column.fieldname === "pending_tasks" && parseInt(value) > 0) {
            value = `<span style="color: red; font-weight: bold;">${value}</span>`;
        }
        
        return value;
    }
};
