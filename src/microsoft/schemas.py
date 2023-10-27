from typing import List

from pydantic import BaseModel, Field


class DateTimeField(BaseModel):
    dateTime: str = Field(
        description="Date and time when the period ends in the format 'YYYY-MM-DDT%H:%m:%s'.")
    timeZone: str = Field(description="Time zone of the end time.")


class GetFreeOrBusySchedule(BaseModel):
    availabilityViewInterval: str = Field(description="Duration of a time slot in an availabilityView")
    EndTime: DateTimeField = Field(description="An object representing the end time and time zone")
    Schedules: List[str] = Field(description="A collection of SMTP addresses of users")
    StartTime: DateTimeField = Field(description="An object representing the start time and time zone")
