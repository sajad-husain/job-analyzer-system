import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = Bot(token=self.bot_token) if self.bot_token else None
        
    async def send_alerts(self, jobs):
        """Send job alerts via Telegram"""
        if not self.bot:
            print("⚠️ Telegram not configured")
            return
            
        for job in jobs:
            message = self._format_job_message(job)
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Failed to send notification: {e}")
    
    def _format_job_message(self, job):
        return f"""
🎯 <b>NEW JOB ALERT!</b>

📋 <b>{job['title']}</b>
🏢 {job.get('company', 'Unknown')}

💰 <b>Pay:</b> ${job['pay_rate']}/hour
📝 <b>Word Count:</b> {job['word_count']} words
⏰ <b>Deadline:</b> {job['deadline']}

🔗 Apply now: {job.get('url', 'Check dashboard')}

#JobAlert #RemoteWork
"""