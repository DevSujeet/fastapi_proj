from pydantic import BaseModel, computed_field
from datetime import datetime
from src.enum.actions import ActionType
from typing import Optional, List

from src.enum.general import AddressType


class Location(BaseModel):
    adbor_id:Optional[str]
    property_name:str
    address_type:Optional[str]
    public_land_address:Optional[str]
    state:Optional[str]
    suburb:Optional[str]
    postalcode:Optional[int]
    submitted_date: Optional[datetime]
    address_type:Optional[AddressType]

    @computed_field(return_type=str)
    def complete_address(self) -> str:
        """Getter for the complete address. this also be part of the json/model dump"""
        return f"{self.public_land_address}, {self.suburb}, {self.state}, {self.postalcode} "
    
    class Config:
        from_attributes = True #'orm_mode' has been renamed to 'from_attributes'
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.timestamp() * 1000,
        }
        allow_extra = True

class LocationRequest(BaseModel):
    '''
    Location request
    '''
    location_column: str # like state, postcode, lga
    location_value: str # like NSW, 2000, Sydney
    location_type: Optional[AddressType]

class BatchLocationRequest(BaseModel):
    '''
    Batch location request
    '''
    user_id: str
    locations: List[LocationRequest]

class LocationResponse(Location):
    location_id:str

    class Config:
        from_attributes = True 
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.timestamp() * 1000,
        }
        allow_extra = True