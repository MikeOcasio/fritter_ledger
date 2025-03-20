import os
import json
from datetime import datetime

class ReferenceManager:
    """Manages reference ID generation and tracking for receipts"""
    
    def __init__(self):
        self.counter_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data',
            'reference_counters.json'
        )
        self.counters = self._load_counters()
        
    def _load_counters(self):
        """Load reference counters from file or create default"""
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.counter_file), exist_ok=True)
        
        if os.path.exists(self.counter_file):
            try:
                with open(self.counter_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading reference counters: {str(e)}")
                return {'receipts': {}}
        else:
            return {'receipts': {}}
    
    def _save_counters(self):
        """Save reference counters to file"""
        try:
            with open(self.counter_file, 'w') as f:
                json.dump(self.counters, f, indent=2)
        except Exception as e:
            print(f"Error saving reference counters: {str(e)}")
    
    def get_next_receipt_reference(self):
        """Generate next receipt reference ID using current date and incrementing counter"""
        today = datetime.now().strftime("%Y%m%d")
        
        # Initialize counter for today if it doesn't exist
        if today not in self.counters['receipts']:
            # Reset all previous day counters when a new day starts
            self.counters['receipts'] = {today: 0}
        
        # Increment counter for today
        self.counters['receipts'][today] += 1
        current_count = self.counters['receipts'][today]
        
        # Save updated counters
        self._save_counters()
        
        # Format: YYYYMMDD-0001, YYYYMMDD-0002, etc.
        return f"{today}-{current_count:04d}"