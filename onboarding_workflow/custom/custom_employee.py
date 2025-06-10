import frappe
from frappe.model.document import Document

@frappe.whitelist()
def create_onboarding_tracker(self, method):
    if frappe.db.exists("Employee Onboarding Tracker", {"employee": self.name}):
        return
    
    template = frappe.get_all("Checklist Template", filters={"job_title": self.job_title}, fields=["name"])
    checklist = []
    email_recipients = []  
    
    if template:
        template_doc = frappe.get_doc("Checklist Template", template[0].name)
        tasks = template_doc.checklist_tasks  
        
        for t in tasks:
            checklist.append({
                "task": t.task,
                "assigned_to": t.default_assignee,
                "is_completed": 0
            })
            
            if t.default_assignee:
                user_email = frappe.db.get_value("User", t.default_assignee, "email")
                if user_email and user_email not in email_recipients:
                    email_recipients.append(user_email)
    
    tracker = frappe.get_doc({
        "doctype": "Employee Onboarding Tracker",
        "employee": self.name,
        "job_title": self.job_title,
        "department": self.department,
        "joining_date": self.date_of_joining,
        "checklist": checklist,
        "status": "Draft"
    })
    tracker.insert(ignore_permissions=True)
    
    if template:
        template_doc = frappe.get_doc("Checklist Template", template[0].name)
        tasks = template_doc.checklist_tasks
        
        user_tasks = {}
        
        for t in tasks:
            if t.default_assignee:
                user_email = frappe.db.get_value("User", t.default_assignee, "email")
                if user_email:
                    if user_email not in user_tasks:
                        user_tasks[user_email] = []
                    user_tasks[user_email].append({
                        'task': t.task,
                        'description': getattr(t, 'description', '')
                    })
        
        for user_email, assigned_tasks in user_tasks.items():
            message_content = f"Please check onboarding tracker for {self.employee_name} ({self.name})\n\nYour Assigned Tasks:\n"
            
            for task in assigned_tasks:
                task_description = task.get('description') or ''
                task_description = task_description.strip() if task_description else ''
                if task_description:
                    message_content += f"- {task['task']}: {task_description}\n"
                else:
                    message_content += f"- {task['task']}: Please complete this onboarding task\n"
            
            frappe.sendmail(
                recipients=[user_email],  
                subject=f"Your Onboarding Tasks: {self.employee_name}",
                message=message_content,
                delayed=False,
                now=True
            )