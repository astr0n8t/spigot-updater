"""
Discord utilities
"""
import discord
from typing import Optional

def create_embed(
    title: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[discord.Color] = None
) -> discord.Embed:
    """Create a Discord embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color or discord.Color.blue()
    )
    return embed

def capitalise(text: str) -> str:
    """Capitalize first letter of text"""
    if not text:
        return text
    return text[0].upper() + text[1:]
