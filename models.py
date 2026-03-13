from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from database import Base
import datetime

class SystemMetric(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    component = Column(String(100), index=True) # e.g., 'database_cluster', 'web_tier'
    metric_name = Column(String(100))           # e.g., 'cpu_usage', 'latency_ms'
    metric_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class SOCAlert(Base):
    __tablename__ = "soc_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    severity = Column(String(50))               # e.g., 'High', 'Medium', 'Low'
    alert_type = Column(String(100))            # e.g., 'Unauthorized Access', 'DDoS'
    description = Column(Text)
    affected_system = Column(String(100))
    resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ERPReport(Base):
    __tablename__ = "erp_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(100))                # e.g., 'Inventory', 'Shipments'
    status = Column(String(50))                 # e.g., 'Delayed', 'On Time'
    impact_description = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
