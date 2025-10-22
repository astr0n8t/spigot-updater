"""
Discord utilities
"""
import discord
from typing import Optional
from datetime import datetime

# Icons for different update types
ICONS = {
    'paper': 'https://avatars.githubusercontent.com/u/7608950?s=200&v=4',
    'spigot': 'https://static.spigotmc.org/img/spigot.png',
    'github': 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png',
    'minecraft': 'https://www.minecraft.net/etc.clientlibs/minecraft/clientlibs/main/resources/img/minecraft-creeper-face.jpg',
    'success': '✅',
    'warning': '⚠️',
    'error': '❌',
    'update': '🆕',
    'server': '🖥️'
}

def create_embed(
    title: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[discord.Color] = None,
    thumbnail: Optional[str] = None,
    image: Optional[str] = None,
    footer_text: Optional[str] = None,
    footer_icon: Optional[str] = None,
    author_name: Optional[str] = None,
    author_icon: Optional[str] = None,
    timestamp: bool = True
) -> discord.Embed:
    """Create a Discord embed with rich formatting
    
    Args:
        title: Embed title
        description: Embed description
        color: Embed color (defaults to blue)
        thumbnail: URL for thumbnail image
        image: URL for main image
        footer_text: Footer text
        footer_icon: Footer icon URL
        author_name: Author name
        author_icon: Author icon URL
        timestamp: Whether to add timestamp (defaults to True)
    
    Returns:
        discord.Embed: Configured embed object
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color or discord.Color.blue(),
        timestamp=datetime.utcnow() if timestamp else None
    )
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    if image:
        embed.set_image(url=image)
    
    if footer_text or footer_icon:
        embed.set_footer(
            text=footer_text or "Spigot Updater Bot",
            icon_url=footer_icon
        )
    
    if author_name:
        embed.set_author(
            name=author_name,
            icon_url=author_icon
        )
    
    return embed

def create_update_embed(
    update_type: str,
    name: str,
    version: Optional[str] = None,
    build: Optional[str] = None,
    description: Optional[str] = None,
    changelog_url: Optional[str] = None,
    affected_servers: Optional[str] = None,
    color: int = 0xFFA500
) -> discord.Embed:
    """Create a rich embed for update notifications
    
    Args:
        update_type: Type of update (paper, spigot, github)
        name: Name of the software/plugin
        version: Version number
        build: Build number (for Paper)
        description: Custom description
        changelog_url: URL to changelog
        affected_servers: List of affected servers
        color: Embed color (defaults to orange)
    
    Returns:
        discord.Embed: Configured update embed
    """
    title = f'{ICONS["update"]} A new version of {name} is available'
    desc = description or 'React with ✅ to approve this update and add it to the queue.'
    
    # Get appropriate icon
    icon = ICONS.get(update_type.lower(), ICONS['minecraft'])
    
    embed = create_embed(
        title=title,
        description=desc,
        color=color,
        thumbnail=icon,
        footer_text="Spigot Updater Bot • React to approve",
        author_name=f"{capitalise(update_type)} Update Available",
        author_icon=icon
    )
    
    if version:
        embed.add_field(name='📦 Version', value=f'`{version}`', inline=True)
    
    if build:
        embed.add_field(name='🔨 Build', value=f'`#{build}`', inline=True)
    
    if changelog_url:
        embed.add_field(name='📝 Changelog', value=f'[View Changelog]({changelog_url})', inline=False)
    
    if affected_servers:
        embed.add_field(name='🖥️ Affected Servers', value=affected_servers, inline=False)
    
    return embed

def create_approval_embed(
    title: str,
    description: str,
    approved_by: Optional[str] = None,
    color: int = 0x00FF00,
    success: bool = True
) -> discord.Embed:
    """Create a rich embed for approval messages
    
    Args:
        title: Embed title
        description: Embed description
        approved_by: User mention who approved
        color: Embed color (defaults to green)
        success: Whether this is a success message
    
    Returns:
        discord.Embed: Configured approval embed
    """
    icon = ICONS['success'] if success else ICONS['error']
    
    if approved_by:
        description = f'{description}\n\n**Approved by:** {approved_by}'
    
    embed = create_embed(
        title=f'{icon} {title}',
        description=description,
        color=color,
        footer_text="Spigot Updater Bot"
    )
    
    return embed

def create_server_update_embed(
    server_name: str,
    current_players: int,
    max_players: int,
    plugins_to_update: list,
    jar_update: bool = False
) -> discord.Embed:
    """Create a rich embed for server update requests
    
    Args:
        server_name: Name of the server
        current_players: Current player count
        max_players: Maximum allowed players for auto-update
        plugins_to_update: List of plugins needing updates
        jar_update: Whether server jar needs updating
    
    Returns:
        discord.Embed: Configured server update embed
    """
    over_limit = current_players > max_players
    
    if over_limit:
        title = f'⚠️ {server_name} needs to update'
        desc = (f'React with ⚠️ to update the server now, whilst there are **{current_players} players online**, '
                f'or react with ❌ to dismiss.')
        color = 0xFF0000  # Red
        thumbnail = None
    else:
        title = f'📣 {server_name} is ready to update'
        desc = (f'React with ✅ to update the server now, whilst there are **{current_players} players online**, '
                f'or react with ❌ to dismiss.')
        color = 0xFFA500  # Orange
        thumbnail = ICONS['server']
    
    embed = create_embed(
        title=title,
        description=desc,
        color=color,
        thumbnail=thumbnail,
        footer_text="Spigot Updater Bot • React to approve or dismiss",
        author_name=f"Server Update: {server_name}",
        author_icon=ICONS['minecraft']
    )
    
    # Add player count info
    player_emoji = '👥'
    status_emoji = '🔴' if over_limit else '🟢'
    embed.add_field(
        name=f'{player_emoji} Players Online',
        value=f'{status_emoji} **{current_players}** / {max_players} allowed for auto-update',
        inline=False
    )
    
    # Add updates info
    if plugins_to_update or jar_update:
        updates = []
        if jar_update:
            updates.append('🎯 **Server JAR**')
        if plugins_to_update:
            updates.append(f'🔌 **Plugins:** {", ".join([f"`{p}`" for p in plugins_to_update])}')
        
        embed.add_field(
            name='📦 Updates Pending',
            value='\n'.join(updates),
            inline=False
        )
    
    return embed

def capitalise(text: str) -> str:
    """Capitalize first letter of text"""
    if not text:
        return text
    return text[0].upper() + text[1:]
