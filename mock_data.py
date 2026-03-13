import datetime
from database import SessionLocal, engine, Base
from models import SystemMetric, SOCAlert, ERPReport

# Create all tables in the database
Base.metadata.create_all(bind=engine)

def generate_mock_data():
    db = SessionLocal()
    
    # Generate System Metrics
    metrics = [
        SystemMetric(component="database_cluster", metric_name="cpu_usage", metric_value=92.5),
        SystemMetric(component="web_tier", metric_name="latency_ms", metric_value=450.0),
        SystemMetric(component="erp_server", metric_name="memory_usage", metric_value=88.1),
    ]
    
    # Generate SOC Alerts
    alerts = [
        SOCAlert(severity="High", alert_type="Brute Force", description="Multiple failed login attempts detected from unknown IP.", affected_system="erp_login"),
        SOCAlert(severity="Medium", alert_type="Unusual Network Traffic", description="Spike in outbound traffic from database cluster.", affected_system="database_cluster")
    ]
    
    # Generate ERP Reports
    reports = [
        ERPReport(module="Shipments", status="Delayed", impact_description="Order processing delayed by 15% due to high database latency."),
        ERPReport(module="Inventory", status="On Time", impact_description="Inventory sync successful.")
    ]
    
    # Add to session
    db.add_all(metrics)
    db.add_all(alerts)
    db.add_all(reports)
    
    try:
        db.commit()
        print("Mock data generated successfully!")
    except Exception as e:
        print(f"Error generating mock data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_mock_data()
