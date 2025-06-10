import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Pending Tasks"), "fieldname": "pending_tasks", "fieldtype": "Int", "width": 100},
        {"label": _("Joining Date"), "fieldname": "joining_date", "fieldtype": "Date", "width": 100}
    ]

def get_data(filters):
    conditions = []
    if filters.get("department"):
        conditions.append("eot.department = %(department)s")
    if filters.get("status"):
        conditions.append("eot.status = %(status)s")

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    else:
        where_clause = "WHERE eot.status IN ('Draft', 'Assigned', 'In Progress')"

    query = f"""
        SELECT 
            eot.employee,
            emp.employee_name,
            eot.department,
            eot.status,
            eot.joining_date,
            COUNT(CASE WHEN ct.is_completed = 0 THEN 1 END) as pending_tasks
        FROM `tabEmployee Onboarding Tracker` eot
        LEFT JOIN `tabEmployee` emp ON eot.employee = emp.name
        LEFT JOIN `tabChecklist Task` ct ON ct.parent = eot.name
        {where_clause}
        GROUP BY eot.name
        ORDER BY eot.joining_date DESC
    """

    return frappe.db.sql(query, filters, as_dict=1)