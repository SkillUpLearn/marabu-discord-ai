import asyncio
import discord
from discord.ext import commands
from google import genai
from google.genai.errors import APIError

# ==================== CONFIGURATION ====================
# Paste your brand new token right here inside the quotes!
RAW_TOKEN = "DISCORD_TOKEN"

GEMINI_API_KEY = "Gemini_API_KEY"
# =======================================================

# This line deletes accidental spaces or extra words at the end
DISCORD_TOKEN = RAW_TOKEN.strip().split(" ")[0]

ai_client = genai.Client(api_key=GEMINI_API_KEY)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!ai ", intents=intents)

@bot.event
async def on_ready():
    print(f"🔒 Bot is secure, timed, and online as {bot.user}")

@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)  # 15 second delay rule
async def chat(ctx, *, prompt: str):
    async with ctx.typing():
        try:
            response = ai_client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            output_text = response.text
            if len(output_text) > 1900:
                for chunk in [output_text[i:i+1900] for i in range(0, len(output_text), 1900)]:
                    await ctx.reply(chunk, mention_author=False)
            else:
                await ctx.reply(output_text, mention_author=False)
        except APIError as api_err:
            if "429" in str(api_err) or "RESOURCE_EXHAUSTED" in str(api_err):
                await ctx.reply("⚠️ Google is currently overwhelmed. Please wait a moment.", mention_author=False)
            else:
                await ctx.reply("❌ Connection error.", mention_author=False)
        except Exception:
            await ctx.reply("❌ System error.", mention_author=False)

@chat.error
async def chat_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(f"⏳ **Slow down!** You can ask another question in **{error.retry_after:.1f} seconds**.", mention_author=False)

bot.run(DISCORD_TOKEN)
