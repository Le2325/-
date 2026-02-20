import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")  # ضع توكن البوت في Environment Variable

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- تحديد الرومات المسموح فيها التيكت ---
ALLOWED_CHANNELS = [
    1474241940030492863,  # ضع هنا ID الروم الأول
    234567890123456789,  # الروم الثاني
    345678901234567890,  # الروم الثالث
    456789012345678901,  # الروم الرابع
    567890123456789012   # الروم الخامس
]

# -------------------------
# زر فتح التذكرة
# -------------------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 فتح تيكت", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # التحقق من الروم المسموح
        if interaction.channel.id not in ALLOWED_CHANNELS:
            await interaction.response.send_message("❌ لا يمكنك فتح تيكت في هذا الروم!", ephemeral=True)
            return

        guild = interaction.guild
        member = interaction.user

        # التأكد من أن العضو ما عنده تيكت مفتوح
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{member.id}")
        if existing:
            await interaction.response.send_message("❌ عندك تيكت مفتوح بالفعل!", ephemeral=True)
            return

        # إنشاء الروم الجديد للتيكت
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{member.id}",
            overwrites=overwrites,
            reason="New Ticket"
        )

        await channel.send(f"🎟️ مرحباً {member.mention}\nاكتب مشكلتك هنا.", view=CloseTicketView())
        await interaction.response.send_message(f"✅ تم إنشاء التيكت: {channel.mention}", ephemeral=True)

# -------------------------
# زر إغلاق التذكرة
# -------------------------
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 إغلاق التيكت", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏳ سيتم حذف التيكت خلال 5 ثواني...")
        await interaction.channel.delete(delay=5)

# -------------------------
# أمر إرسال رسالة التيكت
# -------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    embed = discord.Embed(
        title="📩 نظام التذاكر",
        description="اضغط الزر بالأسفل لفتح تيكت (مسموح فقط في الرومات المحددة)",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())

# -------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)