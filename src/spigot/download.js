const fs = require('fs');

const { path, unzip } = require('../utils/fs');

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

module.exports = async bot => {

	bot.log.info('Clearing temp directory');
	for (const file of fs.readdirSync(path('data/temp/'))) {
		fs.unlinkSync(path('data/temp/' + file));
	}

	let plugins = {};
	Object.keys(bot.config.plugins)
		.filter(plugin => bot.config.plugins[plugin].source.toLowerCase() === 'spigot')
		.filter(async plugin => {
			let p = await bot.db.Plugins.findOne({
				where: {
					name: plugin
				}
			});
			if (!p) return false;
			if (p.get('downloaded') !== p.get('approved')) return true;
		})
		.forEach(plugin => plugins[plugin] = bot.config.plugins[plugin]);
	
	if (plugins.length < 1)
		return bot.log.info('No spigot plugins need to be downloaded, skipping spigot browser');

	bot.log.info('Starting browser');

	const {
		PROXY,
		CHROMEPATH,
	} = process.env;

	let browser;

	if(CHROMEPATH) {
		browser = await puppeteer.launch({
			headless: bot.config.headless_browser,
			executablePath: CHROMEPATH,
			args: [
				bot.config.no_sandbox_browser ? '--no-sandbox' : '',
				PROXY ? '--proxy-server=' + PROXY : ''
			]
		});
	} else {
		browser = await puppeteer.launch({
			headless: bot.config.headless_browser,
			args: [
				bot.config.no_sandbox_browser ? '--no-sandbox' : '',
				PROXY ? '--proxy-server=' + PROXY : ''
			]
		});
	}

	const page = await browser.newPage();
	await page.setDefaultTimeout(bot.config.cloudflare_timeout);
	await page.setDefaultNavigationTimeout(bot.config.cloudflare_timeout);

	await page._client.send('Page.setDownloadBehavior', {
		behavior: 'allow',
		downloadPath: path('data/temp/')
	});

	bot.log.info('Loading spigotmc.org (waiting for Cloudflare)');
	await page.goto('https://www.spigotmc.org/login');
	// await page.waitForTimeout(bot.config.cloudflare_timeout);
	try {
		await page.waitForSelector('#ctrl_pageLogin_login');
	} catch (e) {
		bot.log.info('Screenshotting as error.png');
		await page.screenshot({ path: 'error.png', fullPage: true });
		return bot.log.error(e);
	}
	bot.log.info('Found login page! Saving as loaded.png');
	await page.screenshot({ path: 'loaded.png', fullPage: true });
	await page.waitForTimeout(bot.config.navigation_delay);

	const {
		SPIGOT_EMAIL,
		SPIGOT_PASSWORD
	} = process.env;
	if (SPIGOT_EMAIL && SPIGOT_PASSWORD) {
		bot.log.info('Logging into SpigotMC');
		try {
			await page.type('#ctrl_pageLogin_login', SPIGOT_EMAIL);
		} catch (e) {
			return bot.log.error(e);
		}
		await page.keyboard.press('Tab');
		await page.keyboard.type(SPIGOT_PASSWORD);
		await page.keyboard.press('Tab');
		await page.keyboard.press('Enter');
		try {
			await page.waitForNavigation();
		} catch (e) {
			bot.log.error(e);
		}
		await page.screenshot({ path: 'authenticated.png', fullPage: true });
	} else {
		bot.log.info('Skipping authentication');
	}

	for (const p in plugins) {
		await page.waitForTimeout(bot.config.navigation_delay);
		let plugin = await bot.db.Plugins.findOne({
			where: {
				name: p
			}
		});

		if (!plugin) continue;
		if (plugin.get('downloaded') === plugin.get('approved')) continue;

		if (fs.existsSync(path(`data/plugins/${plugins[p].jar}`)))
			fs.unlinkSync(path(`data/plugins/${plugins[p].jar}`));


		let version = plugin.get('approved');

		let url = `https://www.spigotmc.org/resources/${plugins[p].resource}/download?version=${version}`;

		try {
			bot.log.info(`Downloading ${p} (${version}): plugins/${plugins[p].jar}`);
			await page.goto(url);
		} catch (e) {
			// bot.log.error(e); // it doesn't like downloading
			// continue;
		}

		await page.waitForTimeout(bot.config.download_time);

		let temp = fs.readdirSync(path('data/temp/'));
		if (temp.length < 1) {
			bot.log.warn(`Failed to download ${p}`);
			continue;
		}

		let file = temp[0];

		if (plugins[p].zip_path && file.toLowerCase().endsWith('.zip')) {
			bot.log.info('Extracting...');
			await unzip(
				plugins[p].zip_path,
				path(`data/temp/${file}`),
				path(`data/plugins/${plugins[p].jar}`)
			);
			fs.unlinkSync(path(`data/temp/${file}`));
		} else {
			fs.renameSync(path(`data/temp/${file}`), path(`data/plugins/${plugins[p].jar}`));
		}

		plugin = await plugin.update({
			downloaded: version
		});
	}

	bot.log.info('Closing browser');
	await browser.close();

};