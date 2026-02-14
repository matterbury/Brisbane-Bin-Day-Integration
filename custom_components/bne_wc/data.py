"""The waste collection data received from the BCC API."""

from __future__ import annotations

import math

from dataclasses import dataclass
from datetime import datetime, timedelta, date
from time import strptime

@dataclass
class BccApiData:
    """Object holding the data about waste collection received."""
    # Static, from config.
    property_number: int
    due_in_hours: int
    green_bin: bool
    # Dynamic, fetched from the BCC API.
    suburb: str
    street: str
    house_number: str
    collection_day: str
    collection_zone: int
    recycling_week: bool

    def __init__(self, property_number: int, due_in_hours: int, green_bin: bool):
        """Suppress the auto-generated version that requires all data."""
        self.property_number = property_number
        self.due_in_hours = due_in_hours
        self.green_bin = green_bin

    def collection_week_day(self) -> int | None:
        """Compute the week day number of our collection day."""
        return (None if self.collection_day is None else
                strptime(self.collection_day, '%A').tm_wday)

    def next_collection_date(self) -> datetime | None:
        """Compute the date of the next collection from our collection day."""
        collection_day_no = self.collection_week_day()
        if collection_day_no is None:
            return None
        current_day_no = datetime.today().weekday()
        days_offset = 0 if collection_day_no > current_day_no else 7
        days_to_next_collection = days_offset + collection_day_no - current_day_no
        date_today = datetime.combine(date.today(), datetime.min.time())
        return date_today + timedelta(days=days_to_next_collection)

    def due_in_hours(self) -> int | None:
        """Compute when the next bin collection is due, in hours from now."""
        next_collection_date = self.next_collection_date()
        if next_collection_date is None:
            return None
        diff = next_collection_date - datetime.now()
        return math.ceil(diff.hours) + diff.days * 24

    def extra_bin_text(self) -> str | None:
        """Compute the text describing the next extra bin (Green/Yellow)."""
        return ('Yellow/Recycling' if self.recycling_week else
                'Green/Garden Waste' if self.green_bin else None)

    def is_recycling_week(self) -> bool:
        """Compute whether the next collection includes the recycling bin."""
        return self.recycling_week

    def is_green_waste_week(self) -> bool:
        """Compute whether the next collection includes the green waste bin."""
        return not self.recycling_week
