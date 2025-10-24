"""
Comprehensive observability and audit logging for KarmaChain
Provides detailed logging, metrics, and monitoring capabilities
"""

import logging
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum
import os

# Configure structured logging
class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class EventType(Enum):
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    VALIDATION_ERROR = "validation_error"
    KARMA_ACTION = "karma_action"
    ATONEMENT = "atonement"
    SYSTEM_ERROR = "system_error"
    SECURITY_EVENT = "security_event"
    PERFORMANCE_METRIC = "performance_metric"

@dataclass
class LogEntry:
    """Structured log entry for KarmaChain"""
    timestamp: str
    level: str
    event_type: str
    component: str
    user_id: Optional[str]
    session_id: Optional[str]
    request_id: str
    message: str
    data: Optional[Dict[str, Any]]
    error_details: Optional[Dict[str, Any]]
    performance_metrics: Optional[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class KarmaChainLogger:
    """Comprehensive logging system for KarmaChain"""
    
    def __init__(self, name: str = "KarmaChain", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level))
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Setup handlers
        self._setup_handlers()
        
        # Performance metrics
        self.metrics = {
            'api_requests': 0,
            'validation_errors': 0,
            'system_errors': 0,
            'security_events': 0,
            'karma_actions': 0,
            'atonement_completions': 0,
            'response_times': [],
            'error_breakdown': {}
        }
        
        # Audit trail storage
        self.audit_trail: List[LogEntry] = []
        self.max_audit_entries = 10000
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handlers for different log types
        api_handler = logging.FileHandler("logs/api.log")
        api_handler.setLevel(logging.INFO)
        
        error_handler = logging.FileHandler("logs/errors.log")
        error_handler.setLevel(logging.ERROR)
        
        audit_handler = logging.FileHandler("logs/audit.log")
        audit_handler.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        json_formatter = logging.Formatter('%(message)s')
        
        # Apply formatters
        console_handler.setFormatter(detailed_formatter)
        api_handler.setFormatter(json_formatter)
        error_handler.setFormatter(detailed_formatter)
        audit_handler.setFormatter(json_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(api_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(audit_handler)
    
    def log_api_request(self, request_id: str, method: str, path: str, 
                       user_id: Optional[str] = None, session_id: Optional[str] = None,
                       request_data: Optional[Dict[str, Any]] = None):
        """Log API request"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            event_type=EventType.API_REQUEST.value,
            component="api",
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            message=f"API Request: {method} {path}",
            data={
                "method": method,
                "path": path,
                "request_data": request_data
            },
            error_details=None,
            performance_metrics=None
        )
        
        self._log_entry(entry)
        self.metrics['api_requests'] += 1
    
    def log_api_response(self, request_id: str, status_code: int, 
                        response_time: float, response_data: Optional[Dict[str, Any]] = None):
        """Log API response"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            event_type=EventType.API_RESPONSE.value,
            component="api",
            user_id=None,
            session_id=None,
            request_id=request_id,
            message=f"API Response: {status_code}",
            data={
                "status_code": status_code,
                "response_data": response_data
            },
            error_details=None,
            performance_metrics={
                "response_time_ms": response_time * 1000,
                "status_code": status_code
            }
        )
        
        self._log_entry(entry)
        self.metrics['response_times'].append(response_time)
        
        # Keep only last 1000 response times
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def log_validation_error(self, request_id: str, error_type: str, 
                            field: str, error_message: str, 
                            user_id: Optional[str] = None):
        """Log validation error"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="WARNING",
            event_type=EventType.VALIDATION_ERROR.value,
            component="validation",
            user_id=user_id,
            session_id=None,
            request_id=request_id,
            message=f"Validation failed: {error_message}",
            data={
                "error_type": error_type,
                "field": field,
                "error_message": error_message
            },
            error_details=None,
            performance_metrics=None
        )
        
        self._log_entry(entry)
        self.metrics['validation_errors'] += 1
        
        # Track error breakdown
        error_key = f"{error_type}:{field}"
        self.metrics['error_breakdown'][error_key] = \
            self.metrics['error_breakdown'].get(error_key, 0) + 1
    
    def log_karma_action(self, request_id: str, user_id: str, action: str,
                        karma_impact: float, role: str, intent: str,
                        additional_data: Optional[Dict[str, Any]] = None):
        """Log karma action"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            event_type=EventType.KARMA_ACTION.value,
            component="karma_engine",
            user_id=user_id,
            session_id=None,
            request_id=request_id,
            message=f"Karma action logged: {action}",
            data={
                "action": action,
                "karma_impact": karma_impact,
                "role": role,
                "intent": intent,
                "additional_data": additional_data
            },
            error_details=None,
            performance_metrics=None
        )
        
        self._log_entry(entry)
        self.metrics['karma_actions'] += 1
    
    def log_atonement(self, request_id: str, user_id: str, plan_id: str,
                     atonement_type: str, karma_adjustment: float,
                     paap_reduction: float, success: bool = True):
        """Log atonement completion"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="INFO" if success else "ERROR",
            event_type=EventType.ATONEMENT.value,
            component="atonement",
            user_id=user_id,
            session_id=None,
            request_id=request_id,
            message=f"Atonement {'completed' if success else 'failed'}: {atonement_type}",
            data={
                "plan_id": plan_id,
                "atonement_type": atonement_type,
                "karma_adjustment": karma_adjustment,
                "paap_reduction": paap_reduction,
                "success": success
            },
            error_details=None,
            performance_metrics=None
        )
        
        self._log_entry(entry)
        if success:
            self.metrics['atonement_completions'] += 1
    
    def log_system_error(self, request_id: str, error_type: str, 
                        error_message: str, stack_trace: Optional[str] = None,
                        user_id: Optional[str] = None):
        """Log system error"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="ERROR",
            event_type=EventType.SYSTEM_ERROR.value,
            component="system",
            user_id=user_id,
            session_id=None,
            request_id=request_id,
            message=f"System error: {error_message}",
            data={
                "error_type": error_type,
                "error_message": error_message
            },
            error_details={
                "stack_trace": stack_trace
            },
            performance_metrics=None
        )
        
        self._log_entry(entry)
        self.metrics['system_errors'] += 1
    
    def log_security_event(self, request_id: str, event_type: str, 
                          description: str, severity: str = "medium",
                          user_id: Optional[str] = None, 
                          additional_data: Optional[Dict[str, Any]] = None):
        """Log security event"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="WARNING" if severity in ["low", "medium"] else "ERROR",
            event_type=EventType.SECURITY_EVENT.value,
            component="security",
            user_id=user_id,
            session_id=None,
            request_id=request_id,
            message=f"Security event: {description}",
            data={
                "event_type": event_type,
                "description": description,
                "severity": severity,
                "additional_data": additional_data
            },
            error_details=None,
            performance_metrics=None
        )
        
        self._log_entry(entry)
        self.metrics['security_events'] += 1
    
    def log_performance_metric(self, request_id: str, metric_name: str,
                              value: float, unit: str = "ms",
                              user_id: Optional[str] = None):
        """Log performance metric"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            event_type=EventType.PERFORMANCE_METRIC.value,
            component="performance",
            user_id=user_id,
            session_id=None,
            request_id=request_id,
            message=f"Performance metric: {metric_name} = {value} {unit}",
            data={
                "metric_name": metric_name,
                "value": value,
                "unit": unit
            },
            error_details=None,
            performance_metrics={
                "metric_name": metric_name,
                "value": value,
                "unit": unit
            }
        )
        
        self._log_entry(entry)
    
    def _log_entry(self, entry: LogEntry):
        """Internal method to log entry"""
        # Add to audit trail
        self.audit_trail.append(entry)
        
        # Maintain audit trail size
        if len(self.audit_trail) > self.max_audit_entries:
            self.audit_trail = self.audit_trail[-self.max_audit_entries:]
        
        # Log based on component
        if entry.component == "api":
            self.logger.info(json.dumps(entry.to_dict()))
        elif entry.component == "validation":
            self.logger.warning(json.dumps(entry.to_dict()))
        elif entry.component == "system":
            self.logger.error(json.dumps(entry.to_dict()))
        elif entry.component == "security":
            self.logger.warning(json.dumps(entry.to_dict()))
        else:
            self.logger.info(json.dumps(entry.to_dict()))
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        response_times = self.metrics['response_times']
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            **self.metrics,
            'average_response_time': avg_response_time,
            'total_audit_entries': len(self.audit_trail),
            'uptime_hours': (time.time() - getattr(self, 'start_time', time.time())) / 3600
        }
    
    def get_audit_trail(self, user_id: Optional[str] = None, 
                       event_type: Optional[str] = None,
                       limit: int = 100) -> List[LogEntry]:
        """Get audit trail with optional filtering"""
        filtered_entries = self.audit_trail
        
        if user_id:
            filtered_entries = [entry for entry in filtered_entries 
                                if entry.user_id == user_id]
        
        if event_type:
            filtered_entries = [entry for entry in filtered_entries 
                                if entry.event_type == event_type]
        
        return filtered_entries[-limit:]
    
    def export_audit_trail(self, filename: str, format: str = "json"):
        """Export audit trail to file"""
        if format == "json":
            with open(filename, 'w') as f:
                json.dump([entry.to_dict() for entry in self.audit_trail], f, indent=2)
        elif format == "csv":
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'level', 'event_type', 'component', 
                               'user_id', 'request_id', 'message'])
                for entry in self.audit_trail:
                    writer.writerow([
                        entry.timestamp, entry.level, entry.event_type,
                        entry.component, entry.user_id, entry.request_id,
                        entry.message
                    ])

# Global logger instance
karmachain_logger = KarmaChainLogger()

def log_api_call(func):
    """Decorator to automatically log API calls"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request_id = str(time.time())
        start_time = time.time()
        
        try:
            # Log request
            if hasattr(args[0], 'request'):
                request = args[0].request
                karmachain_logger.log_api_request(
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    user_id=kwargs.get('user_id'),
                    request_data=kwargs
                )
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Log response
            response_time = time.time() - start_time
            karmachain_logger.log_api_response(
                request_id=request_id,
                status_code=200,
                response_time=response_time,
                response_data=result if isinstance(result, dict) else None
            )
            
            return result
            
        except Exception as e:
            # Log error
            response_time = time.time() - start_time
            karmachain_logger.log_system_error(
                request_id=request_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
                user_id=kwargs.get('user_id')
            )
            
            raise
    
    return wrapper

def log_karma_action(func):
    """Decorator to log karma actions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request_id = str(time.time())
        
        try:
            result = await func(*args, **kwargs)
            
            # Log karma action if it has relevant data
            if isinstance(result, dict) and 'karma_impact' in result:
                karmachain_logger.log_karma_action(
                    request_id=request_id,
                    user_id=kwargs.get('user_id'),
                    action=kwargs.get('action', 'unknown'),
                    karma_impact=result.get('karma_impact', 0),
                    role=kwargs.get('role', 'unknown'),
                    intent=kwargs.get('intent', 'unknown'),
                    additional_data=result
                )
            
            return result
            
        except Exception as e:
            karmachain_logger.log_system_error(
                request_id=request_id,
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=kwargs.get('user_id')
            )
            raise
    
    return wrapper