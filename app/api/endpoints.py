from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
import os

from ..services.gamification import GamificationService
from ..services.strava_service import StravaService
from ..db.session import get_db
from ..models.user import User
from ..models.activity import Activity
from ..auth.dependencies import get_current_user
from ..schemas.location import LocationUpdate
from ..schemas.user import UserCreate, UserResponse

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

@router.post("/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/user/stats", response_model=UserResponse)
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """Get user's gamification stats."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "total_distance": float(current_user.total_distance or 0.0),
        "total_co2_saved": float(current_user.total_co2_saved or 0.0),
        "points": int(current_user.points or 0),
        "strava_connected": bool(current_user.strava_connected or False)
    }

@router.get("/strava/auth")
async def strava_auth(current_user: User = Depends(get_current_user)):
    """Get Strava authorization URL."""
    strava = StravaService()
    # Create a state token with the user's email
    state = jwt.encode({"sub": current_user.email}, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    # Use Vercel URL for callback
    callback_url = os.getenv("VERCEL_URL", "http://localhost:8000")
    auth_url = await strava.get_oauth_url(f"{callback_url}/api/strava/callback", state)
    return {"auth_url": auth_url}

@router.get("/strava/callback")
async def strava_callback(
    code: str,
    state: str = "",
    db: Session = Depends(get_db)
):
    """Handle Strava OAuth callback."""
    # Get the token from the state if provided
    user_email = None
    try:
        if state:
            payload = jwt.decode(state, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
            user_email = payload.get("sub")
    except:
        pass
    
    # If no email in state, try to get it from the token exchange
    if not user_email:
        strava = StravaService()
        token_response = await strava.exchange_token(code)
        if "error" in token_response:
            raise HTTPException(status_code=400, detail=token_response["error"])
        
        # Get or create user based on Strava athlete ID
        athlete_id = str(token_response["athlete"]["id"])
        user = db.query(User).filter(User.strava_athlete_id == athlete_id).first()
        
        if not user:
            # Try to find by email
            athlete_email = token_response["athlete"].get("email")
            if athlete_email:
                user = db.query(User).filter(User.email == athlete_email).first()
            
            if not user:
                raise HTTPException(status_code=400, detail="Please register or login first")
    else:
        # Get user by email
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        strava = StravaService()
        token_response = await strava.exchange_token(code)
        if "error" in token_response:
            raise HTTPException(status_code=400, detail=token_response["error"])
    
    # Update user's Strava credentials
    user.strava_connected = True
    user.strava_access_token = token_response["access_token"]
    user.strava_refresh_token = token_response["refresh_token"]
    user.strava_token_expires_at = token_response["expires_at"]
    user.strava_athlete_id = str(token_response["athlete"]["id"])
    
    # Store the connection timestamp to only sync activities after this point
    user.strava_connected_at = datetime.utcnow()
    
    db.commit()
    
    # Don't sync historical activities, we'll only sync new ones
    # that happen after the connection timestamp
    
    # Redirect to frontend dashboard with location permission request
    from fastapi.responses import RedirectResponse
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return RedirectResponse(url=f"{frontend_url}/dashboard?requestLocation=true")

@router.get("/strava/webhook")
async def strava_webhook_verify(
    hub_mode: str = Query(...),
    hub_verify_token: str = Query(...),
    hub_challenge: str = Query(...)
):
    """Handle Strava webhook verification."""
    strava = StravaService()
    if not strava.verify_webhook(hub_mode, hub_verify_token):
        raise HTTPException(status_code=400, detail="Invalid verification token")
    return {"hub.challenge": hub_challenge}

@router.post("/strava/webhook")
async def strava_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Strava webhook events."""
    event = await request.json()
    print(f"Received Strava webhook event: {event}")
    
    # Get user by Strava athlete ID
    user = db.query(User).filter(User.strava_athlete_id == str(event["owner_id"])).first()
    if not user:
        print(f"User not found for Strava athlete ID: {event['owner_id']}")
        return {"message": "User not found"}
    
    # Only process activities that happened after Strava connection
    if not user.strava_connected_at:
        print(f"No connection timestamp found for user: {user.email}")
        return {"message": "No connection timestamp found"}
        
    activity_start = datetime.fromtimestamp(event["object_id"])
    if activity_start < user.strava_connected_at:
        print(f"Activity {event['object_id']} is before Strava connection time")
        return {"message": "Activity is before Strava connection"}
    
    strava = StravaService()
    activity = await strava.get_activity(event["object_id"], user.strava_access_token)
    if not activity:
        print(f"Failed to fetch activity {event['object_id']} from Strava")
        return {"message": "Activity not found"}
    
    print(f"Retrieved activity from Strava: {activity}")
    
    # Skip if already synced
    if str(activity["id"]) in (user.synced_activities or []):
        print(f"Activity {activity['id']} already synced")
        return {"message": "Activity already synced"}
    
    # Convert Strava activity to our format
    if activity["type"] == "Walk":
        transport_mode = "WALKING"
        co2_saved = activity["distance"] * 0.2  # 200g CO2 saved per km vs driving
    elif activity["type"] == "Run":
        transport_mode = "RUNNING"
        co2_saved = activity["distance"] * 0.2  # 200g CO2 saved per km vs driving
    elif activity["type"] == "Ride":
        transport_mode = "CYCLING"
        co2_saved = activity["distance"] * 0.2  # 200g CO2 saved per km vs driving
    else:
        print(f"Unsupported activity type: {activity['type']}")
        return {"message": "Unsupported activity type"}
    
    print(f"Processing activity: type={transport_mode}, distance={activity['distance']}, co2_saved={co2_saved}")
    
    # Create activity
    db_activity = Activity(
        user_id=user.id,
        activity_type=transport_mode,
        distance=activity["distance"],
        duration=activity["moving_time"],
        carbon_impact=co2_saved,
        start_time=datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%SZ"),
        end_time=datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=activity["moving_time"])
    )
    db.add(db_activity)
    
    # Update user stats
    user.total_distance = (user.total_distance or 0.0) + activity["distance"]
    user.total_co2_saved = (user.total_co2_saved or 0.0) + co2_saved
    if user.synced_activities is None:
        user.synced_activities = []
    user.synced_activities.append(str(activity["id"]))
    
    # Calculate and add points
    gamification = GamificationService()
    points = gamification.calculate_points(
        distance=activity["distance"],
        duration=activity["moving_time"],
        transport_mode=transport_mode
    )
    user.points = (user.points or 0) + points
    
    print(f"Updated user stats: distance={user.total_distance}, co2_saved={user.total_co2_saved}, points={user.points}")
    
    db.commit()
    return {"message": "Activity processed successfully"}

@router.post("/user/location")
async def update_user_location(
    location: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's location."""
    current_user.latitude = location.latitude
    current_user.longitude = location.longitude
    current_user.location_updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Location updated successfully"}

@router.post("/user/reset-stats")
async def reset_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset user's stats to start fresh."""
    current_user.total_distance = 0.0
    current_user.total_co2_saved = 0.0
    current_user.points = 0
    current_user.synced_activities = []
    current_user.achievements = []
    current_user.strava_connected_at = datetime.utcnow()  # Reset connection time to now
    
    # Delete all activities
    db.query(Activity).filter(Activity.user_id == current_user.id).delete()
    
    db.commit()
    return {"message": "Stats reset successfully"}

@router.get("/activities")
async def get_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's activities."""
    activities = db.query(Activity).filter(
        Activity.user_id == current_user.id
    ).order_by(Activity.start_time.desc()).all()
    
    return [{
        "id": activity.id,
        "activity_type": activity.activity_type,
        "description": f"{activity.activity_type.title()} activity",
        "distance": activity.distance,
        "duration": activity.duration,
        "carbon_impact": activity.carbon_impact,
        "timestamp": activity.start_time.isoformat(),
    } for activity in activities]

@router.post("/strava/create-webhook")
async def create_strava_webhook():
    """Create Strava webhook subscription."""
    strava = StravaService()
    callback_url = os.getenv("VERCEL_URL", "http://localhost:8000")
    result = await strava.create_webhook_subscription(f"{callback_url}/api/strava/webhook")
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create webhook subscription")
    return {"message": "Webhook subscription created successfully", "result": result}
