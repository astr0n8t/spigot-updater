"""
Check for updates across all sources
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from paper.check import check as paper_check
from github.check import check as github_check
from spigot.check import check as spigot_check
from bukkit.check import check as bukkit_check
from jenkins.check import check as jenkins_check
from serverjars.check import check as serverjars_check

async def check_for_updates(bot):
    """Check all sources for updates"""
    await paper_check(bot)
    await serverjars_check(bot)
    await github_check(bot)
    await jenkins_check(bot)
    await spigot_check(bot)
    await bukkit_check(bot)
