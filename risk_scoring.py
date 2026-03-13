from models import SystemMetric, SOCAlert, ERPReport

def calculate_risk_score(metrics: list, alerts: list, reports: list) -> dict:
    """
    Evaluates current metrics, alerts, and reports to determine business risk.
    """
    base_score = 0
    anomalies = []
    
    # 1. Evaluate Alerts
    for alert in alerts:
        if alert.severity == "High":
            base_score += 40
            anomalies.append(f"Critical SOC Alert: {alert.alert_type} on {alert.affected_system}")
        elif alert.severity == "Medium":
            base_score += 20

    # 2. Evaluate Metrics
    for metric in metrics:
        if metric.metric_name == "cpu_usage" and metric.metric_value > 85.0:
            base_score += 30
            anomalies.append(f"High CPU Usage: {metric.metric_value}% on {metric.component}")
        elif metric.metric_name == "latency_ms" and metric.metric_value > 300.0:
            base_score += 25
            anomalies.append(f"High Latency: {metric.metric_value}ms on {metric.component}")

    # 3. Evaluate ERP Reports
    for report in reports:
        if report.status == "Delayed":
            base_score += 35
            anomalies.append(f"ERP Delay: {report.module} - {report.impact_description}")

    # Normalize score
    normalized_score = min(base_score, 100)
    
    risk_level = "Low"
    if normalized_score >= 70:
        risk_level = "High"
    elif normalized_score >= 40:
        risk_level = "Medium"

    return {
        "risk_score": normalized_score,
        "risk_level": risk_level,
        "anomalies_detected": anomalies
    }

def get_current_business_health(db):
    metrics = db.query(SystemMetric).all()
    alerts = db.query(SOCAlert).filter(SOCAlert.resolved == False).all()
    reports = db.query(ERPReport).all()
    
    return calculate_risk_score(metrics, alerts, reports)
