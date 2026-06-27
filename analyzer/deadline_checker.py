from datetime import datetime, timedelta
from typing import Dict, List
import json
import os

class DeadlineChecker:
    def __init__(self):
        # Load your existing deadlines/calendar
        self.existing_commitments = self._load_calendar()
        
    def _load_calendar(self):
        """Load your existing deadlines and commitments"""
        # This could be from a calendar API, database, or config file
        return {
            '2026-07-10': ['Job A - Final Draft', 'Meeting 2pm'],
            '2026-07-12': ['Job B - Revisions'],
            '2026-07-15': ['Job C - Research Phase'],
        }
    
    def has_conflict(self, new_deadline: str) -> bool:
        """Check if new deadline conflicts with existing commitments"""
        # Parse dates
        try:
            new_date = datetime.strptime(new_deadline, '%Y-%m-%d').date()
        except ValueError:
            # Try other formats
            return False
        
        # Check for conflicts (including 2-day buffer)
        buffer_days = 2
        for existing_date_str in self.existing_commitments.keys():
            existing_date = datetime.strptime(existing_date_str, '%Y-%m-%d').date()
            
            # Check if deadlines are within buffer period
            if abs((new_date - existing_date).days) < buffer_days:
                return True
                
        return False
    
    def add_commitment(self, date: str, description: str):
        """Add a new commitment to calendar"""
        if date in self.existing_commitments:
            self.existing_commitments[date].append(description)
        else:
            self.existing_commitments[date] = [description]
        
        # Save to persistent storage
        self._save_calendar()
    
    def _save_calendar(self):
        """Persist calendar data"""
        import os
        # Ensure config directory exists
        os.makedirs('config', exist_ok=True)
        with open('config/calendar.json', 'w') as f:
            json.dump(self.existing_commitments, f)