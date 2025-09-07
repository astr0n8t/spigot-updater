const { EmbedBuilder } = require('discord.js');
const config = require('../../config/config');

let bot;

module.exports = {
	init: b => bot = b,
	Embed: class Embed extends EmbedBuilder {
		constructor(data) {
			super(Object.assign({
				color: config.color,
				/* footer: {
					text: `${config.server_name} automatic updater`,
					iconURL: bot.user.displayAvatarURL(),
				} */
			}, data));
		}

	},
	createEmbed(data) {
		return new this.Embed(data);
	},
	
};