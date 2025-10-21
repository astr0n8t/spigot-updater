"""
SpigotMC download module
"""
import os
import sys
import asyncio
import zipfile
import re
from pathlib import Path
from playwright.async_api import async_playwright
from playwright_stealth import stealth

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.fs import path

async def download(bot):
    """Download approved SpigotMC plugins"""
    bot.log.info('Clearing temp directory')
    temp_dir = Path(path('data/temp/'))
    for file in temp_dir.iterdir():
        if file.is_file():
            file.unlink()
    
    # Get plugins that need to be downloaded
    session_db = bot.db['Session']()
    try:
        plugin_names = [k for k, v in bot.config['plugins'].items()
                       if v.get('source', '').lower() == 'spigot']
        
        # Filter to only plugins that need downloading
        plugins_to_download = []
        for plugin_name in plugin_names:
            plugin = session_db.query(bot.db['Plugins']).filter_by(name=plugin_name).first()
            if plugin and plugin.approved and plugin.downloaded != plugin.approved:
                plugins_to_download.append(plugin_name)
        
        if not plugins_to_download:
            return bot.log.info('No SpigotMC plugins need to be downloaded, skipping spigot browser')
        
        plugins = {name: bot.config['plugins'][name] for name in plugins_to_download}
    finally:
        session_db.close()
    
    bot.log.info('Starting browser')
    
    # Get environment variables
    proxy = os.getenv('PROXY')
    chrome_path = os.getenv('CHROMEPATH')
    spigot_email = os.getenv('SPIGOT_EMAIL')
    spigot_password = os.getenv('SPIGOT_PASSWORD')
    
    async with async_playwright() as p:
        # Launch browser
        launch_options = {
            'headless': bot.config.get('headless_browser', True),
            'args': []
        }
        
        if bot.config.get('no_sandbox_browser', False):
            launch_options['args'].append('--no-sandbox')
        
        if proxy:
            launch_options['args'].append(f'--proxy-server={proxy}')
        
        if chrome_path:
            launch_options['executable_path'] = chrome_path
        
        browser = await p.chromium.launch(**launch_options)
        
        # Create context with downloads enabled
        context = await browser.new_context(
            accept_downloads=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Apply stealth to avoid detection
        await stealth(page)
        
        # Set timeouts
        page.set_default_timeout(bot.config.get('cloudflare_timeout', 300000))
        page.set_default_navigation_timeout(bot.config.get('cloudflare_timeout', 300000))
        
        try:
            await page.wait_for_timeout(bot.config.get('navigation_delay', 10000))
            bot.log.info('Loading spigotmc.org (waiting for Cloudflare)')
            await page.goto('https://www.spigotmc.org/login')
            
            # Wait for page to load
            await page.wait_for_selector('.spigot_colorOverlay', timeout=bot.config.get('cloudflare_timeout', 300000))
            bot.log.info('Loaded spigotmc.org! Saving screenshot as loaded.png...')
            await page.wait_for_timeout(bot.config.get('navigation_delay', 10000))
            await page.screenshot(path='loaded.png', full_page=True)
            
            # Check if we need to log in
            if page.url.endswith('login'):
                bot.log.info('Found login page, attempting to log in...')
                
                if spigot_email and spigot_password:
                    bot.log.info('Logging into SpigotMC')
                    try:
                        await page.fill('#ctrl_pageLogin_login', spigot_email)
                        await page.keyboard.press('Tab')
                        await page.keyboard.type(spigot_password)
                        await page.keyboard.press('Tab')
                        await page.keyboard.press('Enter')
                        
                        try:
                            await page.wait_for_load_state('networkidle', timeout=30000)
                        except Exception as e:
                            bot.log.error(f'Navigation error: {e}')
                        
                        bot.log.info('Logged in, screenshot saved as authenticated.png')
                        await page.screenshot(path='authenticated.png', full_page=True)
                    except Exception as e:
                        bot.log.error(f'Login error: {e}')
                        return
                else:
                    bot.log.info('Skipping authentication')
            else:
                bot.log.info('Already logged in!')
            
            # Download each plugin
            for plugin_name, plugin_config in plugins.items():
                bot.log.info(f"Updating download for '{plugin_config['jar']}'")
                
                try:
                    session_db = bot.db['Session']()
                    try:
                        plugin = session_db.query(bot.db['Plugins']).filter_by(name=plugin_name).first()
                        
                        if not plugin:
                            continue
                        if plugin.downloaded == plugin.approved:
                            continue
                        
                        # Remove old jar if exists
                        jar_path = Path(path(f"data/plugins/{plugin_config['jar']}"))
                        if jar_path.exists():
                            jar_path.unlink()
                        
                        version = plugin.approved
                        resource_id = plugin_config.get('resource')
                        download_url = f'https://www.spigotmc.org/resources/{resource_id}/download?version={version}'
                        
                        await page.wait_for_timeout(bot.config.get('navigation_delay', 10000))
                        bot.log.info(f'Downloading {plugin_name} ({version}): plugins/{plugin_config["jar"]}')
                        
                        # Start download
                        try:
                            async with page.expect_download() as download_info:
                                await page.goto(download_url)
                                download = await download_info.value
                                
                                # Save to temp directory
                                temp_file = temp_dir / download.suggested_filename
                                await download.save_as(temp_file)
                        except Exception as e:
                            # Sometimes the download doesn't trigger the expect_download event
                            # Just wait and check if file appeared
                            await page.wait_for_timeout(bot.config.get('download_time', 10000))
                        
                        # Check if file was downloaded
                        temp_files = list(temp_dir.iterdir())
                        if not temp_files:
                            bot.log.warning(f'Failed to download {plugin_name}')
                            continue
                        
                        downloaded_file = temp_files[0]
                        
                        # Handle zip extraction if needed
                        if plugin_config.get('zip_path') and downloaded_file.suffix.lower() == '.zip':
                            bot.log.info('Extracting...')
                            zip_path_pattern = plugin_config['zip_path']
                            
                            with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
                                # List all files in zip
                                for file_info in zip_ref.filelist:
                                    # Check if file matches pattern
                                    if isinstance(zip_path_pattern, str) and zip_path_pattern.startswith('r'):
                                        # It's a regex pattern (stored as string starting with 'r')
                                        pattern = re.compile(zip_path_pattern.strip('r').strip("'").strip('"'))
                                        if pattern.match(file_info.filename):
                                            zip_ref.extract(file_info, temp_dir)
                                            extracted_file = temp_dir / file_info.filename
                                            extracted_file.rename(jar_path)
                                            break
                                    else:
                                        # Exact match
                                        if file_info.filename == zip_path_pattern:
                                            zip_ref.extract(file_info, temp_dir)
                                            extracted_file = temp_dir / file_info.filename
                                            extracted_file.rename(jar_path)
                                            break
                            
                            downloaded_file.unlink()
                        else:
                            # Just rename the file
                            downloaded_file.rename(jar_path)
                        
                        # Update database
                        plugin.downloaded = version
                        session_db.commit()
                        bot.log.success(f'Downloaded {plugin_name} ({version})')
                    
                    finally:
                        session_db.close()
                
                except Exception as e:
                    bot.log.warning('Could not download plugin!')
                    bot.log.error(f'Error: {e}')
        
        except Exception as e:
            bot.log.info('Screenshotting as error.png')
            await page.screenshot(path='error.png', full_page=True)
            bot.log.error(f'Error: {e}')
        
        finally:
            bot.log.info('Closing browser')
            await browser.close()
