"""
Check for updates across all sources
"""
from paper import check as paper_check
from github import check as github_check
from spigot import check as spigot_check
from bukkit import check as bukkit_check
from jenkins import check as jenkins_check
from serverjars import check as serverjars_check

async def check_for_updates(bot):
    """Check all sources for updates"""
    await paper_check.check(bot)
    await serverjars_check.check(bot)
    await github_check.check(bot)
    await jenkins_check.check(bot)
    await spigot_check.check(bot)
    await bukkit_check.check(bot)
