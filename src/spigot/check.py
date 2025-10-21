"""
SpigotMC update checker (requires web scraping)
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
from playwright_stealth import stealth

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.discord_utils import create_embed

async def check(bot):
    """Check for SpigotMC plugin updates"""
    plugins = {k: v for k, v in bot.config['plugins'].items()
               if v.get('source', '').lower() == 'spigot'}
    
    if not plugins:
        return bot.log.info('No SpigotMC plugins need to be checked, skipping spigot browser')
    
    bot.log.info('Checking for updates for plugins on SpigotMC')
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
        
        # Create context with user data directory
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Apply stealth to avoid detection
        await stealth(page)
        
        # Set timeouts
        page.set_default_timeout(bot.config.get('cloudflare_timeout', 300000))
        page.set_default_navigation_timeout(bot.config.get('cloudflare_timeout', 300000))
        
        try:
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
            
            # Check each plugin
            for plugin_name, plugin_config in plugins.items():
                bot.log.info(f"Checking '{plugin_config['jar']}'")
                
                try:
                    await page.wait_for_timeout(bot.config.get('navigation_delay', 10000))
                    resource_id = plugin_config.get('resource')
                    await page.goto(f'https://www.spigotmc.org/resources/{resource_id}/updates')
                    await page.wait_for_selector('.downloadButton > a')
                    
                    # Get the download URL and extract version
                    download_url = await page.evaluate('() => document.querySelector(".downloadButton > a").href')
                    parsed_url = urlparse(download_url)
                    query_params = parse_qs(parsed_url.query)
                    latest = query_params.get('version', [None])[0]
                    
                    if not latest:
                        bot.log.warning(f"Couldn't find a version number for {plugin_name}")
                        continue
                    
                    # Check database
                    session_db = bot.db['Session']()
                    try:
                        plugin = session_db.query(bot.db['Plugins']).filter_by(name=plugin_name).first()
                        
                        if not plugin:
                            plugin = bot.db['Plugins'](name=plugin_name)
                            session_db.add(plugin)
                        
                        if plugin.approved == latest:
                            continue
                        
                        # Update latest version
                        plugin.latest = latest
                        session_db.commit()
                        
                        bot.log.info(f"Found an update for '{plugin_config['jar']}'")
                        
                        # Find affected servers
                        affected = ', '.join([f'`{s}`' for s, cfg in bot.config['servers'].items()
                                            if plugin_name in cfg.get('plugins', [])])
                        
                        # Send Discord notification
                        embed = create_embed(
                            title=f'🆕 A new version of {plugin_name} is available',
                            description='React with ✅ to approve this update and add it to the queue.',
                            color=0xFFA500  # Orange
                        )
                        embed.add_field(name='Changelog', 
                                      value=f'[View updates on SpigotMC](https://www.spigotmc.org/resources/{resource_id}/updates)',
                                      inline=False)
                        embed.add_field(name='Affected servers', 
                                      value=f'Servers using this plugin:\n{affected}',
                                      inline=False)
                        embed.set_footer(text=f'SpigotMC version {latest}')
                        
                        msg = await bot.channel.send(embed=embed)
                        await msg.add_reaction('✅')
                        
                        bot.messages[msg.id] = {
                            'plugin': {
                                'name': plugin_name,
                                'version': latest
                            }
                        }
                    finally:
                        session_db.close()
                
                except Exception as e:
                    bot.log.warning('Could not check plugin!')
                    bot.log.error(f'Error: {e}')
        
        except Exception as e:
            bot.log.info('Screenshotting as error.png')
            await page.screenshot(path='error.png', full_page=True)
            bot.log.error(f'Error loading SpigotMC: {e}')
        
        finally:
            bot.log.info('Closing browser')
            await browser.close()
