from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class DateTimeField(BaseModel):
    dateTime: str = Field(
        description="Date and time when the period ends in the format 'YYYY-MM-DDT%H:%m:%s'.")
    timeZone: str = Field(description="Time zone of the end time.")


class GetFreeOrBusySchedule(BaseModel):
    availabilityViewInterval: int = Field(description="Duration of a time slot in an availabilityView")
    endTime: DateTimeField = Field(description="An object representing the end time and time zone")
    schedules: List[str] = Field(description="A collection of SMTP addresses of users")
    startTime: DateTimeField = Field(description="An object representing the start time and time zone")
