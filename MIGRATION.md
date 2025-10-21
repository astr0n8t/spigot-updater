# Migration from Node.js to Python

This document describes the migration from the Node.js version to the Python implementation.

## Overview

The entire codebase has been reimplemented in Python while maintaining the same functionality and architecture as the original Node.js version.

## What's Changed

### Technology Stack
- **Language**: Node.js → Python 3.12+
- **Discord Library**: discord.js → discord.py
- **Database ORM**: Sequelize → SQLAlchemy
- **Web Scraping**: Puppeteer → Playwright
- **HTTP Library**: node-fetch → aiohttp
- **Minecraft Status**: minecraft-server-util → mcstatus

### File Structure
All source files have been moved from JavaScript to Python:
- `src/*.js` → `src/*.py`
- Configuration files: `config/*.js` → `config/*.py`

### Configuration Changes

**Important naming changes:**
- In `servers.py`: `host` is now called `address` for clarity
- In `plugins.py`: `repository` is now called `repo` for consistency

## Migration Steps

If you're upgrading from the Node.js version:

1. **Backup your data**:
   ```bash
   cp -r data data.backup
   ```

2. **Update configuration files**:
   ```bash
   # Rename and convert your config files
   cp config/example-config.py config/config.py
   cp config/example-servers.py config/servers.py
   cp config/example-plugins.py config/plugins.py
   ```

3. **Edit the new Python config files** based on your old JavaScript configs:
   - Change `module.exports = {` to just the variable definition
   - Change `host:` to `address:` in servers
   - Change `repository:` to `repo:` in plugins
   - Remove trailing commas if they cause issues
   - Use Python syntax (True/False instead of true/false)

4. **Keep your environment file**:
   Your `.env` file doesn't need any changes!

5. **Rebuild Docker container**:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Implementation Status

### ✅ Fully Implemented
- **Paper**: Full support for checking and downloading Paper server JARs
- **GitHub**: Full support for plugins from GitHub Releases
- **Discord Bot**: Complete Discord integration with reaction handling
- **Pterodactyl**: Full API client implementation
- **Database**: SQLAlchemy ORM with SQLite support
- **Update Workflow**: Complete check, download, and upload cycle

### ⚠️ Partially Implemented
- **SpigotMC**: Structure in place, requires Playwright browser automation setup
- **Bukkit**: Placeholder only, needs implementation
- **Jenkins**: Placeholder only, needs implementation  
- **ServerJars**: Placeholder only, needs implementation

### Implementation Notes

The core functionality (Paper servers + GitHub plugins) is fully working. Additional sources can be implemented following the same pattern as Paper and GitHub.

## Database Compatibility

The SQLite database schema is compatible between Node.js and Python versions. Your existing `data/database.sqlite` will work without modifications.

## Dependencies

### Python Requirements
All Python dependencies are listed in `requirements.txt`:
- discord.py >= 2.3.2
- python-dotenv >= 1.0.0
- aiohttp >= 3.9.0
- aiofiles >= 23.2.1
- requests >= 2.31.0
- sqlalchemy >= 2.0.23
- aiosqlite >= 0.19.0
- playwright >= 1.40.0
- mcstatus >= 11.1.1

### Docker
The Dockerfile has been updated to use Python 3.12 and includes:
- All Python dependencies
- Playwright with Chromium browser
- Same security and resource configurations as before

## Testing

After migration, test that:
1. The bot connects to Discord successfully
2. Update checks work for your configured sources
3. Download tasks complete successfully
4. Upload workflow functions correctly
5. Reaction-based approvals work

## Known Limitations

1. SpigotMC web scraping needs Playwright browser setup (Cloudflare protection)
2. Some sources (Bukkit, Jenkins, ServerJars) are not yet fully implemented
3. The bot maintains the same behavior and should be transparent to end users

## Getting Help

If you encounter issues during migration:
1. Check logs for error messages
2. Verify your config files are valid Python syntax
3. Ensure environment variables are set correctly
4. Compare with the example config files

## Future Enhancements

Potential improvements for future versions:
- Complete SpigotMC implementation with Playwright
- Add ServerJars API support
- Implement Jenkins build server support
- Add Bukkit/BukkitDev support
- Enhanced error handling and retry logic
- More detailed logging options
