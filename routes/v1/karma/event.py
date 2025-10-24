from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from datetime import datetime
import uuid

# Import database and models
from database import karma_events_col
from models import KarmaEvent

# Import internal route handlers
from routes.v1.karma.log_action import log_action, LogActionRequest
from routes.v1.karma.appeal import appeal_karma, appeal_status, AppealRequest
from routes.v1.karma.atonement import submit_atonement, submit_atonement_with_file, AtonementSubmission
from routes.v1.karma.death import death_event, DeathEventRequest
from routes.v1.karma.stats import get_user_stats

router = APIRouter()

class UnifiedEventRequest(BaseModel):
    type: str = Field(..., description="Event type: life_event, atonement, appeal, death_event, stats_request")
    data: Dict[str, Any] = Field(..., description="Event-specific data payload")
    timestamp: Optional[datetime] = None
    source: Optional[str] = Field(None, description="Source system or department")

class UnifiedEventResponse(BaseModel):
    status: str
    event_type: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    routing_info: Dict[str, Any]

@router.post("/", response_model=UnifiedEventResponse)
async def unified_event_endpoint(request: UnifiedEventRequest):
    """
    Unified event gateway that routes different event types to appropriate internal endpoints.
    Stores all events in karma_events collection for audit and debugging.
    
    Purpose: Allows other departments to trigger karmic actions via one standard gateway.
    
    Event Types:
    - life_event: Log user actions (maps to /log-action)
    - atonement: Submit atonement proof (maps to /atonement/submit)
    - appeal: Request karma appeal (maps to /appeal)
    - death_event: Process user death (maps to /death/event)
    - stats_request: Get user statistics (maps to /stats)
    """
    # Generate unique event ID
    event_id = str(uuid.uuid4())
    
    # Set default timestamp if not provided
    if not request.timestamp:
        request.timestamp = datetime.utcnow()
    
    # Initialize database event record
    db_event = KarmaEvent(
        event_id=event_id,
        event_type=request.type,
        data=request.data,
        timestamp=request.timestamp,
        source=request.source,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    try:
        # Route based on event type
        if request.type == "life_event":
            response = await _handle_life_event(request, event_id)
        elif request.type == "atonement":
            response = await _handle_atonement(request, event_id)
        elif request.type == "appeal":
            response = await _handle_appeal(request, event_id)
        elif request.type == "death_event":
            response = await _handle_death_event(request, event_id)
        elif request.type == "stats_request":
            response = await _handle_stats_request(request, event_id)
        else:
            # Update database with error
            db_event.status = "failed"
            db_event.error_message = f"Invalid event type: {request.type}"
            karma_events_col.insert_one(db_event.dict())
            
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid event type: {request.type}. Valid types: life_event, atonement, appeal, death_event, stats_request"
            )
        
        # Update database with success
        db_event.status = "processed"
        db_event.response_data = response.dict()
        db_event.updated_at = datetime.utcnow()
        karma_events_col.insert_one(db_event.dict())
        
        return response
        
    except HTTPException as e:
        # Update database with HTTP error
        db_event.status = "failed"
        db_event.error_message = str(e)
        db_event.updated_at = datetime.utcnow()
        karma_events_col.insert_one(db_event.dict())
        raise
    except Exception as e:
        # Update database with unexpected error
        db_event.status = "failed"
        db_event.error_message = f"Internal error: {str(e)}"
        db_event.updated_at = datetime.utcnow()
        karma_events_col.insert_one(db_event.dict())
        
        raise HTTPException(
            status_code=500, 
            detail=f"Internal error processing {request.type}: {str(e)}"
        )

async def _handle_life_event(request: UnifiedEventRequest, event_id: str) -> UnifiedEventResponse:
    """Handle life_event type - maps to log_action endpoint"""
    try:
        # Validate required fields
        if "user_id" not in request.data or "action" not in request.data or "role" not in request.data:
            raise HTTPException(status_code=400, detail="life_event requires user_id, action, and role in data")
        
        # Create LogActionRequest
        log_request = LogActionRequest(
            user_id=request.data["user_id"],
            action=request.data["action"],
            role=request.data["role"],
            note=request.data.get("note"),
            context=request.data.get("context"),
            metadata=request.data.get("metadata")
        )
        
        # Call internal endpoint
        result = log_action(log_request)
        
        return UnifiedEventResponse(
            status="success",
            event_type="life_event",
            message="Life event logged successfully",
            data=result,
            timestamp=request.timestamp,
            routing_info={
                "internal_endpoint": "/v1/karma/log-action/",
                "mapped_from": "life_event"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing life_event: {str(e)}")

async def _handle_atonement(request: UnifiedEventRequest, event_id: str) -> UnifiedEventResponse:
    """Handle atonement type - maps to atonement submission"""
    try:
        # Validate required fields
        required_fields = ["user_id", "plan_id", "atonement_type", "amount"]
        for field in required_fields:
            if field not in request.data:
                raise HTTPException(status_code=400, detail=f"atonement requires {field} in data")
        
        # Create AtonementSubmission
        atonement_request = AtonementSubmission(
            user_id=request.data["user_id"],
            plan_id=request.data["plan_id"],
            atonement_type=request.data["atonement_type"],
            amount=request.data["amount"],
            proof_text=request.data.get("proof_text"),
            tx_hash=request.data.get("tx_hash")
        )
        
        # Call internal endpoint
        result = await submit_atonement(atonement_request)
        
        return UnifiedEventResponse(
            status="success",
            event_type="atonement",
            message="Atonement submitted successfully",
            data=result,
            timestamp=request.timestamp,
            routing_info={
                "internal_endpoint": "/v1/karma/atonement/submit",
                "mapped_from": "atonement"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing atonement: {str(e)}")

async def _handle_appeal(request: UnifiedEventRequest, event_id: str) -> UnifiedEventResponse:
    """Handle appeal type - maps to appeal endpoint"""
    try:
        # Validate required fields
        if "user_id" not in request.data or "action" not in request.data:
            raise HTTPException(status_code=400, detail="appeal requires user_id and action in data")
        
        # Create AppealRequest
        appeal_request = AppealRequest(
            user_id=request.data["user_id"],
            action=request.data["action"],
            context=request.data.get("context")
        )
        
        # Call internal endpoint
        result = await appeal_karma(appeal_request)
        
        return UnifiedEventResponse(
            status="success",
            event_type="appeal",
            message="Appeal submitted successfully",
            data=result,
            timestamp=request.timestamp,
            routing_info={
                "internal_endpoint": "/v1/karma/appeal/",
                "mapped_from": "appeal"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing appeal: {str(e)}")

async def _handle_death_event(request: UnifiedEventRequest, event_id: str) -> UnifiedEventResponse:
    """Handle death_event type - maps to death event endpoint"""
    try:
        # Validate required fields
        if "user_id" not in request.data:
            raise HTTPException(status_code=400, detail="death_event requires user_id in data")
        
        # Create DeathEventRequest
        death_request = DeathEventRequest(
            user_id=request.data["user_id"]
        )
        
        # Call internal endpoint
        result = await death_event(death_request)
        
        return UnifiedEventResponse(
            status="success",
            event_type="death_event",
            message="Death event processed successfully",
            data=result,
            timestamp=request.timestamp,
            routing_info={
                "internal_endpoint": "/v1/karma/death/event",
                "mapped_from": "death_event"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing death_event: {str(e)}")

async def _handle_stats_request(request: UnifiedEventRequest, event_id: str) -> UnifiedEventResponse:
    """Handle stats_request type - maps to stats endpoint"""
    try:
        # Validate required fields
        if "user_id" not in request.data:
            raise HTTPException(status_code=400, detail="stats_request requires user_id in data")
        
        # Call internal endpoint
        result = await get_user_stats(request.data["user_id"])
        
        return UnifiedEventResponse(
            status="success",
            event_type="stats_request",
            message="User statistics retrieved successfully",
            data=result,
            timestamp=request.timestamp,
            routing_info={
                "internal_endpoint": "/v1/karma/stats/{user_id}",
                "mapped_from": "stats_request"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing stats_request: {str(e)}")

# Additional endpoint for file-based atonement submissions
@router.post("/with-file", response_model=UnifiedEventResponse)
async def unified_event_with_file(
    event_type: str = Form(..., description="Event type (currently only 'atonement_with_file' supported)"),
    user_id: str = Form(...),
    plan_id: str = Form(...),
    atonement_type: str = Form(...),
    amount: float = Form(...),
    proof_text: Optional[str] = Form(None),
    tx_hash: Optional[str] = Form(None),
    proof_file: Optional[UploadFile] = File(None)
):
    """
    Unified event gateway for file-based submissions.
    Currently supports atonement submissions with file uploads.
    """
    event_id = str(uuid.uuid4())
    
    # Create database event record
    db_event = KarmaEvent(
        event_id=event_id,
        event_type=event_type,
        data={
            "user_id": user_id,
            "plan_id": plan_id,
            "atonement_type": atonement_type,
            "amount": amount,
            "proof_text": proof_text,
            "tx_hash": tx_hash,
            "has_file": True,
            "file_name": proof_file.filename if proof_file else None
        },
        timestamp=datetime.utcnow(),
        source="unified_event_with_file",
        status="pending",
        created_at=datetime.utcnow()
    )
    
    try:
        if event_type != "atonement_with_file":
            # Update database with error
            db_event.status = "failed"
            db_event.error_message = "Currently only 'atonement_with_file' is supported for file uploads"
            karma_events_col.insert_one(db_event.dict())
            raise HTTPException(status_code=400, detail="Currently only 'atonement_with_file' is supported for file uploads")
        
        # Call the file-based atonement endpoint
        result = await submit_atonement_with_file(
            user_id=user_id,
            plan_id=plan_id,
            atonement_type=atonement_type,
            amount=amount,
            proof_text=proof_text,
            tx_hash=tx_hash,
            proof_file=proof_file
        )
        
        # Update database with success
        db_event.status = "processed"
        db_event.response_data = result
        db_event.updated_at = datetime.utcnow()
        karma_events_col.insert_one(db_event.dict())
        
        return UnifiedEventResponse(
            status="success",
            event_type=event_type,
            message="Atonement with file submitted successfully",
            data=result,
            timestamp=datetime.utcnow(),
            routing_info={
                "internal_endpoint": "/v1/karma/atonement/submit-with-file",
                "mapped_from": event_type
            }
        )
        
    except HTTPException as e:
        # Update database with HTTP error
        db_event.status = "failed"
        db_event.error_message = str(e)
        db_event.updated_at = datetime.utcnow()
        karma_events_col.insert_one(db_event.dict())
        raise
    except Exception as e:
        # Update database with unexpected error
        db_event.status = "failed"
        db_event.error_message = f"Internal error: {str(e)}"
        db_event.updated_at = datetime.utcnow()
        karma_events_col.insert_one(db_event.dict())
        raise HTTPException(status_code=500, detail=f"Error processing {event_type}: {str(e)}")