"""
Workflow Templates
Pre-built workflow templates for common use cases
"""

from datetime import datetime

from src.workflows.workflow_engine import Connection, Workflow
from src.workflows.workflow_nodes import create_node


class WorkflowTemplates:
    """Pre-built workflow templates"""

    @staticmethod
    def create_daily_reminder_workflow() -> Workflow:
        """Daily reminder workflow"""
        workflow = Workflow(
            workflow_id=f"template_daily_reminder_{datetime.now().timestamp()}",
            name="Daily Reminder",
            description="Sends daily reminder notifications",
        )

        # Timer trigger
        trigger = create_node("trigger.timer")
        trigger.config["interval_seconds"] = 86400  # 24 hours
        trigger.position = {"x": 100, "y": 100}
        workflow.add_node(trigger)

        # Send notification
        notify = create_node("action.send_notification")
        notify.position = {"x": 400, "y": 100}
        workflow.add_node(notify)

        # Set notification content
        notify.input_ports[1].default_value = "Daily Reminder"
        notify.input_ports[2].default_value = "Don't forget to review your goals!"

        # Connect
        conn = Connection(
            "conn_1",
            trigger.node_id,
            "exec",
            notify.node_id,
            "exec",
        )
        workflow.add_connection(conn)

        return workflow

    @staticmethod
    def create_task_automation_workflow() -> Workflow:
        """Automated task creation workflow"""
        workflow = Workflow(
            workflow_id=f"template_task_automation_{datetime.now().timestamp()}",
            name="Task Automation",
            description="Automatically creates tasks based on events",
        )

        # Event trigger
        trigger = create_node("trigger.event")
        trigger.config["event_type"] = "email_received"
        trigger.position = {"x": 100, "y": 100}
        workflow.add_node(trigger)

        # Create task
        task = create_node("action.create_task")
        task.position = {"x": 400, "y": 100}
        workflow.add_node(task)

        # Set task details
        task.input_ports[1].default_value = "Follow up on email"
        task.input_ports[2].default_value = "Reply to important email"
        task.input_ports[3].default_value = "high"

        # Connect
        conn = Connection(
            "conn_1",
            trigger.node_id,
            "exec",
            task.node_id,
            "exec",
        )
        workflow.add_connection(conn)

        # Log completion
        log = create_node("utility.log")
        log.position = {"x": 700, "y": 100}
        log.input_ports[1].default_value = "Task created from email"
        workflow.add_node(log)

        conn2 = Connection(
            "conn_2",
            task.node_id,
            "exec",
            log.node_id,
            "exec",
        )
        workflow.add_connection(conn2)

        return workflow

    @staticmethod
    def create_conditional_notification_workflow() -> Workflow:
        """Conditional notification based on comparison"""
        workflow = Workflow(
            workflow_id=f"template_conditional_{datetime.now().timestamp()}",
            name="Conditional Notification",
            description="Sends notification based on condition",
        )

        # Manual trigger
        trigger = create_node("trigger.manual")
        trigger.position = {"x": 100, "y": 100}
        workflow.add_node(trigger)

        # Get variable
        get_var = create_node("data.get_variable")
        get_var.config["variable_name"] = "task_count"
        get_var.position = {"x": 300, "y": 80}
        workflow.add_node(get_var)

        # Compare
        compare = create_node("logic.compare")
        compare.config["operator"] = ">"
        compare.input_ports[1].default_value = 10  # Compare to 10
        compare.position = {"x": 500, "y": 100}
        workflow.add_node(compare)

        # If node
        if_node = create_node("logic.if")
        if_node.position = {"x": 700, "y": 100}
        workflow.add_node(if_node)

        # Notification (true branch)
        notify_high = create_node("action.send_notification")
        notify_high.position = {"x": 900, "y": 50}
        notify_high.input_ports[1].default_value = "High Task Count"
        notify_high.input_ports[2].default_value = "You have many tasks pending!"
        notify_high.input_ports[3].default_value = "high"
        workflow.add_node(notify_high)

        # Notification (false branch)
        notify_low = create_node("action.send_notification")
        notify_low.position = {"x": 900, "y": 150}
        notify_low.input_ports[1].default_value = "Normal Task Count"
        notify_low.input_ports[2].default_value = "Task count is under control"
        notify_low.input_ports[3].default_value = "normal"
        workflow.add_node(notify_low)

        # Connections
        connections = [
            Connection("conn_1", trigger.node_id, "exec", if_node.node_id, "exec"),
            Connection("conn_2", if_node.node_id, "true", notify_high.node_id, "exec"),
            Connection("conn_3", if_node.node_id, "false", notify_low.node_id, "exec"),
        ]

        for conn in connections:
            workflow.add_connection(conn)

        return workflow

    @staticmethod
    def create_ai_email_response_workflow() -> Workflow:
        """AI-powered email response workflow"""
        workflow = Workflow(
            workflow_id=f"template_ai_email_{datetime.now().timestamp()}",
            name="AI Email Response",
            description="Generates AI response for emails",
        )

        # Event trigger
        trigger = create_node("trigger.event")
        trigger.config["event_type"] = "email_received"
        trigger.position = {"x": 100, "y": 100}
        workflow.add_node(trigger)

        # Sentiment analysis
        sentiment = create_node("ai.sentiment_analysis")
        sentiment.position = {"x": 350, "y": 100}
        workflow.add_node(sentiment)

        # AI text generation
        ai_gen = create_node("ai.text_generation")
        ai_gen.position = {"x": 600, "y": 100}
        ai_gen.input_ports[1].default_value = "Generate a professional email response"
        workflow.add_node(ai_gen)

        # Send email
        send_email = create_node("action.send_email")
        send_email.position = {"x": 850, "y": 100}
        workflow.add_node(send_email)

        # Connections
        connections = [
            Connection("conn_1", trigger.node_id, "exec", sentiment.node_id, "exec"),
            Connection("conn_2", sentiment.node_id, "exec", ai_gen.node_id, "exec"),
            Connection("conn_3", ai_gen.node_id, "exec", send_email.node_id, "exec"),
        ]

        for conn in connections:
            workflow.add_connection(conn)

        return workflow

    @staticmethod
    def create_productivity_monitor_workflow() -> Workflow:
        """Productivity monitoring workflow"""
        workflow = Workflow(
            workflow_id=f"template_productivity_{datetime.now().timestamp()}",
            name="Productivity Monitor",
            description="Monitors and logs productivity metrics",
        )

        # Timer trigger (hourly)
        trigger = create_node("trigger.timer")
        trigger.config["interval_seconds"] = 3600  # 1 hour
        trigger.position = {"x": 100, "y": 100}
        workflow.add_node(trigger)

        # Get productivity score
        get_score = create_node("data.get_variable")
        get_score.config["variable_name"] = "productivity_score"
        get_score.position = {"x": 350, "y": 100}
        workflow.add_node(get_score)

        # Set variable (log score)
        set_var = create_node("data.set_variable")
        set_var.config["variable_name"] = "last_productivity_score"
        set_var.position = {"x": 600, "y": 100}
        workflow.add_node(set_var)

        # Log
        log = create_node("utility.log")
        log.position = {"x": 850, "y": 100}
        log.input_ports[1].default_value = "Productivity score logged"
        workflow.add_node(log)

        # Compare for low productivity
        compare = create_node("logic.compare")
        compare.config["operator"] = "<"
        compare.input_ports[1].default_value = 50
        compare.position = {"x": 600, "y": 250}
        workflow.add_node(compare)

        # If low productivity
        if_node = create_node("logic.if")
        if_node.position = {"x": 850, "y": 250}
        workflow.add_node(if_node)

        # Alert notification
        alert = create_node("action.send_notification")
        alert.position = {"x": 1100, "y": 250}
        alert.input_ports[1].default_value = "Low Productivity Alert"
        alert.input_ports[2].default_value = "Your productivity is below target"
        alert.input_ports[3].default_value = "warning"
        workflow.add_node(alert)

        # Connections
        connections = [
            Connection("conn_1", trigger.node_id, "exec", set_var.node_id, "exec"),
            Connection("conn_2", set_var.node_id, "exec", log.node_id, "exec"),
            Connection("conn_3", log.node_id, "exec", if_node.node_id, "exec"),
            Connection("conn_4", if_node.node_id, "true", alert.node_id, "exec"),
        ]

        for conn in connections:
            workflow.add_connection(conn)

        return workflow

    @staticmethod
    def get_all_templates():
        """Get all available templates"""
        return [
            {
                "name": "Daily Reminder",
                "description": "Sends daily reminder notifications",
                "factory": WorkflowTemplates.create_daily_reminder_workflow,
            },
            {
                "name": "Task Automation",
                "description": "Automatically creates tasks from events",
                "factory": WorkflowTemplates.create_task_automation_workflow,
            },
            {
                "name": "Conditional Notification",
                "description": "Sends notifications based on conditions",
                "factory": WorkflowTemplates.create_conditional_notification_workflow,
            },
            {
                "name": "AI Email Response",
                "description": "Generates AI-powered email responses",
                "factory": WorkflowTemplates.create_ai_email_response_workflow,
            },
            {
                "name": "Productivity Monitor",
                "description": "Monitors and alerts on productivity metrics",
                "factory": WorkflowTemplates.create_productivity_monitor_workflow,
            },
        ]
