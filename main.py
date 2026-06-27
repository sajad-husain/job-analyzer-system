#!/usr/bin/env python3
import asyncio
import logging
from scheduler.job_scheduler import JobMonitorScheduler
from word_automation.macro_handler import WordMacroHandler
from ai_integration.editgpt_client import EditGPTClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)

async def main():
    print("🚀 Starting Job Monitor System v1.0")
    print("=" * 50)
    
    # Initialize Word automation if needed
    print("📄 Checking Word integration...")
    word_handler = WordMacroHandler()
    word_handler.test_connection()
    
    # Initialize editGPT
    print("🤖 Initializing editGPT integration...")
    ai_client = EditGPTClient()
    if ai_client.is_available():
        print("✅ editGPT ready")
    
    # Start the scheduler
    print("⏰ Starting 30-second job monitor...")
    scheduler = JobMonitorScheduler()
    scheduler.start()
    
    # Keep running
    print("\n✅ System running. Press Ctrl+C to stop.\n")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        scheduler.scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())