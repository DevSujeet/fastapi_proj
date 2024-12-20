from fastapi import APIRouter, Depends
from fastapi.logger import logger
from typing import Dict
from src.models.UserActivity import UserActivityBase, ActionType
from datetime import datetime
from typing import List
from src.services.userActivity import insert_user_activity, get_activities_by_userid, get_all_user_activities
from sqlmodel import Session
from src.db import get_session

router = APIRouter(
    prefix="/activity",
    tags=["activity"],
    dependencies=[Depends(get_session)],
    responses={404: {"description": "X_ProjectID field is required in header"}}
)

# ACTIVITIES = [
#     UserActivityBase(user_id='1',record_name="abc.pdf",data_category='govt',action=ActionType.EDIT,timestamp=datetime.now()),
#     UserActivityBase(user_id='2',record_name="bsd.pdf",data_category='pvt',action=ActionType.CREATE,timestamp=datetime.now()),
#     UserActivityBase(user_id='3',record_name="ert.pdf",data_category='public',action=ActionType.UPLOAD,timestamp=datetime.now()),
#     UserActivityBase(user_id='4',record_name="fgt.pdf",data_category='govt',action=ActionType.DELETE,timestamp=datetime.now()),
# ]

@router.get('/all')
async def all_users_activities(session:Session = Depends(get_session)) -> List[UserActivityBase]:
    return get_all_user_activities(session=session)
    

@router.get('/byUser')
async def activity_by_user(user_id:str,session:Session = Depends(get_session)) -> UserActivityBase:
    # return user for a given user_id
    return get_activities_by_userid(user_id=user_id,session=session)

@router.post('')
async def create_user_activity(activity:UserActivityBase, session:Session = Depends(get_session)):
    insert_user_activity(activity=activity, session=session)