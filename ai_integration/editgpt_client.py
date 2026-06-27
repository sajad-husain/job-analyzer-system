"""
editGPT Client - Placeholder
Will be implemented when AI integration is needed
"""

class EditGPTClient:
    def __init__(self):
        self.available = False
        print("🤖 EditGPTClient initialized (placeholder)")
        
    def is_available(self):
        return self.available
        
    def analyze_job(self, job_description):
        print(f"🤖 Would analyze: {job_description[:50]}...")
        return {"score": 0.85, "summary": "Sample analysis"}