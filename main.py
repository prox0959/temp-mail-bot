import os
import random
import string
import asyncio
from typing import Optional, Dict

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks

ADMIN_ID = 
PANEL_CHANNEL_ID = 
CATEGORY_ID = 
MAILTM_BASE = "https://api.mail.tm"
TOKEN = ""  # set your bot token here


def random_string(length: int = 10) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


class MailTmClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_domain(self) -> str:
        async with self.session.get(f"{MAILTM_BASE}/domains") as resp:
            data = await resp.json()
            if resp.status != 200 or "hydra:member" not in data or not data["hydra:member"]:
                raise RuntimeError("No domains available from mail.tm")
            return data["hydra:member"][0]["domain"]

    async def create_account(self, address: str, password: str) -> Dict:
        async with self.session.post(
            f"{MAILTM_BASE}/accounts",
            json={"address": address, "password": password},
        ) as resp:
            data = await resp.json()
            if resp.status not in (200, 201):
                raise RuntimeError(data.get("message", "Failed to create account"))
            return data

    async def get_token(self, address: str, password: str) -> str:
        async with self.session.post(
            f"{MAILTM_BASE}/token",
            json={"address": address, "password": password},
        ) as resp:
            data = await resp.json()
            if resp.status != 200 or "token" not in data:
                raise RuntimeError(data.get("message", "Failed to get token"))
            return data["token"]

    async def list_messages(self, token: str) -> Dict:
        headers = {"Authorization": f"Bearer {token}"}
        async with self.session.get(f"{MAILTM_BASE}/messages", headers=headers) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(data.get("message", "Failed to fetch messages"))
            return data

    async def delete_message(self, token: str, message_id: str) -> None:
        headers = {"Authorization": f"Bearer {token}"}
        async with self.session.delete(f"{MAILTM_BASE}/messages/{message_id}", headers=headers) as resp:
            if resp.status not in (200, 204):
                data = await resp.json()
                raise RuntimeError(data.get("message", "Failed to delete message"))

    async def get_message(self, token: str, message_id: str) -> Dict:
        headers = {"Authorization": f"Bearer {token}"}
        async with self.session.get(f"{MAILTM_BASE}/messages/{message_id}", headers=headers) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(data.get("message", "Failed to fetch message"))
            return data

    async def delete_account(self, token: str, account_id: str) -> None:
        headers = {"Authorization": f"Bearer {token}"}
        async with self.session.delete(f"{MAILTM_BASE}/accounts/{account_id}", headers=headers) as resp:
            if resp.status not in (200, 202, 204):
                data = await resp.json()
                raise RuntimeError(data.get("message", "Failed to delete account"))


class TempMailBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.session: Optional[aiohttp.ClientSession] = None
        self.mailtm: Optional[MailTmClient] = None
        self.user_accounts: Dict[int, list] = {}
        self.channel_accounts: Dict[int, Dict] = {}

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self.mailtm = MailTmClient(self.session)
        self.tree.add_command(inbox_command)
        self.tree.add_command(delete_command)
        self.add_view(PanelView(self))
        self.add_view(DeleteAccountView(self))
        self.poll_messages.start()

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

    async def on_ready(self):
        await self.tree.sync()
        await self.ensure_panel()
        print(f"Logged in as {self.user}")

    async def ensure_panel(self):
        channel = self.get_channel(PANEL_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            return
        async for message in channel.history(limit=50):
            if message.author == self.user and message.embeds:
                if message.embeds[0].title == "Temp Mail Service":
                    return
        embed = discord.Embed(
            title="Temp Mail Service",
            description=(
                "🇬🇧 Click the button below to generate your private temp email inbox.\n"
                "🇹🇷 Özel geçici e-posta kutunuzu oluşturmak için aşağıdaki butona tıklayın."
            ),
            color=discord.Color.green(),
        )
        view = PanelView(self)
        await channel.send(embed=embed, view=view)

    @tasks.loop(seconds=30)
    async def poll_messages(self):
        await self.wait_until_ready()
        if not self.mailtm:
            return
        for channel_id, account in list(self.channel_accounts.items()):
            token = account.get("token")
            user_id = account.get("owner_id")
            if not token or not user_id:
                continue
            channel = self.get_channel(channel_id)
            if not isinstance(channel, discord.TextChannel):
                continue
            try:
                data = await self.mailtm.list_messages(token)
            except Exception:
                continue
            messages = data.get("hydra:member", [])
            seen_ids = account.setdefault("seen_ids", set())
            new_messages = [m for m in messages if m.get("id") not in seen_ids]
            if not new_messages:
                continue
            for msg in reversed(new_messages):
                msg_id = msg.get("id")
                if not msg_id:
                    continue
                try:
                    full = await self.mailtm.get_message(token, msg_id)
                except Exception:
                    continue
                seen_ids.add(msg_id)
                await self.send_full_message(channel, user_id, full)

    async def send_full_message(self, channel: discord.TextChannel, user_id: int, message_data: Dict):
        sender = message_data.get("from", {}).get("address", "Unknown")
        subject = message_data.get("subject", "(No subject)")
        intro = message_data.get("intro") or ""
        text_body = message_data.get("text") or ""
        if not text_body:
            text_body = intro or "(No content)"
        if len(text_body) > 3800:
            text_body = text_body[:3800] + "..."
        embed = discord.Embed(
            title=subject,
            description=text_body,
            color=discord.Color.green(),
        )
        embed.add_field(name="From", value=sender, inline=True)
        message_id = message_data.get("id", "?")
        embed.set_footer(text=f"Message ID: {message_id}")
        mention = f"<@{user_id}>"
        await channel.send(content=mention, embed=embed)


class PanelView(discord.ui.View):
    def __init__(self, bot: TempMailBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Create Temp Mail / Oluştur", style=discord.ButtonStyle.success, custom_id="temp_mail_create")
    async def create_temp(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not self.bot.mailtm:
            await interaction.followup.send("Mail service not ready.", ephemeral=True)
            return

        try:
            is_admin = interaction.user.id == ADMIN_ID
            if not is_admin:
                existing = self.bot.user_accounts.get(interaction.user.id, [])
                if existing:
                    await interaction.followup.send("You already have a temp mail channel. Only admins can create multiple.", ephemeral=True)
                    return

            domain = await self.bot.mailtm.get_domain()
            local = random_string(10)
            address = f"{local}@{domain}"
            password = random_string(16)
            account = await self.bot.mailtm.create_account(address, password)
            token = await self.bot.mailtm.get_token(address, password)

            guild = interaction.guild
            if not guild:
                await interaction.followup.send("Guild not found.", ephemeral=True)
                return

            category = guild.get_channel(CATEGORY_ID)
            if not isinstance(category, discord.CategoryChannel):
                await interaction.followup.send("Category not found.", ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            }

            admin_member = guild.get_member(ADMIN_ID)
            if admin_member:
                overwrites[admin_member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

            suffix = random_string(4)
            channel_name = f"temp-mail-{interaction.user.name}-{suffix}".lower().replace(" ", "-")
            temp_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

            account_entry = {
                "owner_id": interaction.user.id,
                "address": address,
                "password": password,
                "token": token,
                "account_id": account.get("id"),
                "channel_id": temp_channel.id,
                "seen_ids": set(),
            }

            self.bot.user_accounts.setdefault(interaction.user.id, []).append(account_entry)
            self.bot.channel_accounts[temp_channel.id] = account_entry

            embed = discord.Embed(
                title="Your Temp Mail Inbox",
                description=(
                    f"🇬🇧 Email Address: {address}\n"
                    "New emails will be delivered here automatically. Use /delete to remove messages or the button below to close this inbox.\n\n"
                    f"🇹🇷 E-posta Adresi: {address}\n"
                    "Yeni e-postalar otomatik olarak buraya düşer. Mesaj silmek için /delete komutunu veya aşağıdaki butonu kullanın."
                ),
                color=discord.Color.green(),
            )
            view = DeleteAccountView(self.bot)
            msg = await temp_channel.send(content=interaction.user.mention, embed=embed, view=view)
            await msg.pin()

            await interaction.followup.send(f"Your temp mail channel has been created: {temp_channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Unexpected error: {e}", ephemeral=True)


class DeleteAccountView(discord.ui.View):
    def __init__(self, bot: TempMailBot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Delete Temp Mail / Sil", style=discord.ButtonStyle.danger, custom_id="temp_mail_delete")
    async def delete_temp(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            account = self.bot.channel_accounts.get(interaction.channel_id)
            if not account:
                await interaction.followup.send("No temp mail account found for this channel.", ephemeral=True)
                return

            owner_id = account.get("owner_id")
            if interaction.user.id != owner_id and interaction.user.id != ADMIN_ID:
                await interaction.followup.send("Only the owner or admin can delete this temp mail.", ephemeral=True)
                return

            if not self.bot.mailtm:
                await interaction.followup.send("Mail service not ready.", ephemeral=True)
                return

            account_id = account.get("account_id")
            token = account.get("token")
            if account_id and token:
                await self.bot.mailtm.delete_account(token, account_id)

            owner_accounts = self.bot.user_accounts.get(owner_id, [])
            owner_accounts = [a for a in owner_accounts if a.get("channel_id") != interaction.channel_id]
            if owner_accounts:
                self.bot.user_accounts[owner_id] = owner_accounts
            else:
                self.bot.user_accounts.pop(owner_id, None)

            self.bot.channel_accounts.pop(interaction.channel_id, None)

            await interaction.followup.send("Temp mail account deleted. This channel will be removed.", ephemeral=True)
            channel = interaction.channel
            if isinstance(channel, discord.TextChannel):
                await asyncio.sleep(2)
                await channel.delete()
        except Exception as e:
            await interaction.followup.send(f"Unexpected error: {e}", ephemeral=True)


async def get_user_account(interaction: discord.Interaction) -> Optional[Dict]:
    bot: TempMailBot = interaction.client  # type: ignore
    account = bot.channel_accounts.get(interaction.channel_id)
    if not account:
        await interaction.response.send_message("This command must be used inside your temp mail channel.", ephemeral=True)
        return None
    owner_id = account.get("owner_id")
    if interaction.user.id != owner_id and interaction.user.id != ADMIN_ID:
        await interaction.response.send_message("You don't have access to this temp mail channel.", ephemeral=True)
        return None
    return account


@app_commands.command(name="inbox", description="Fetch your temp mail inbox")
async def inbox_command(interaction: discord.Interaction):
    account = await get_user_account(interaction)
    if not account:
        return

    bot: TempMailBot = interaction.client  # type: ignore
    try:
        data = await bot.mailtm.list_messages(account["token"])  # type: ignore
    except Exception as e:
        await interaction.response.send_message(f"Failed to fetch inbox: {e}", ephemeral=True)
        return

    messages = data.get("hydra:member", [])
    if not messages:
        await interaction.response.send_message("Your inbox is empty.", ephemeral=True)
        return

    embed = discord.Embed(title="Inbox", color=discord.Color.blurple())
    for msg in messages[:10]:
        sender = msg.get("from", {}).get("address", "Unknown")
        subject = msg.get("subject", "(No subject)")
        preview = msg.get("intro", "No preview")
        message_id = msg.get("id", "?")
        embed.add_field(
            name=f"{subject} (ID: {message_id})",
            value=f"From: {sender}\n{preview}",
            inline=False,
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@app_commands.command(name="delete", description="Delete messages from your temp inbox")
@app_commands.describe(message_id="Message ID to delete or 'all' to delete everything")
async def delete_command(interaction: discord.Interaction, message_id: Optional[str] = None):
    account = await get_user_account(interaction)
    if not account:
        return

    bot: TempMailBot = interaction.client  # type: ignore

    try:
        if message_id and message_id.lower() == "all":
            data = await bot.mailtm.list_messages(account["token"])  # type: ignore
            messages = data.get("hydra:member", [])
            if not messages:
                await interaction.response.send_message("Inbox is already empty.", ephemeral=True)
                return
            for msg in messages:
                await bot.mailtm.delete_message(account["token"], msg["id"])  # type: ignore
            await interaction.response.send_message("All messages deleted.", ephemeral=True)
            return

        if not message_id:
            await interaction.response.send_message("Provide a message ID or 'all'.", ephemeral=True)
            return

        await bot.mailtm.delete_message(account["token"], message_id)  # type: ignore
        await interaction.response.send_message(f"Deleted message {message_id}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete message: {e}", ephemeral=True)


def main():
    token = TOKEN or os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Set TOKEN in main.py or DISCORD_TOKEN environment variable")

    bot = TempMailBot()
    bot.add_view(PanelView(bot))
    bot.add_view(DeleteAccountView(bot))
    bot.run(token)


if __name__ == "__main__":
    main()
