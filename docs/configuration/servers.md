# Servers

The servers configuration file, [`config/servers.yaml`](https://github.com/Left4Craft/spigot-updater/blob/master/config/servers.yaml).
This file should contain a YAML structure of server objects:

```yaml
ServerName:
  address: String  # optional
  left4status: String  # optional
  pterodactyl_id: String
  jar:
    type: String
    version: String
  max_players: Number
  plugins:
    - PluginName1
    - PluginName2
```

## Server properties

??? summary "host"
	### address

	:octicons-info-24: Conditionally optional
	{: .details }

	:octicons-checklist-24: Type: `String`
	{: .details }

	**One of `address` or `left4status` is required**.

	The address of this server to be queried for the player count, such as `mc.left4craft.org` or `mc.left4craft.org:25565`.

	**Note**: This was previously called `host` in older versions.

??? summary "left4status"
	### left4status

	:octicons-info-24: Conditionally optional
	{: .details }

	:octicons-checklist-24: Type: `String`
	{: .details }

	**One of `address` or `left4status` is required**.

	The ID of the server in the response to be returned from Left4Status. If you set this option, you must also set [`left4status` in `config.yaml`](../config/#left4status).

	This option can be used if your internal servers can not be queried externally.

??? summary "pterodactyl_id"
	### pterodactyl_id

	:octicons-checklist-24: Type: `String`
	{: .details }

	The (short) ID of the Pterodactyl server. Used for interfacing with the Pterodactyl API when uploading files.

??? summary "jar"
	### jar

	:octicons-checklist-24: Type: `Object`
	{: .details }

	An object describing the server jar.

	???+ summary "type"
		#### type

		:octicons-checklist-24: Type: `String`
		{: .details }

		The server type, such as `paper`, `spigot`, and `bungeecord`. Must be a supported server type from the API you chose for [`server_jars_api` in `config.yaml`](../config/#server_jars_api).

	???+ summary "version"
		#### version

		:octicons-checklist-24: Type: `String`
		{: .details }

		The server version, such as `1.16`, or for `serverjars` - `1.16.4` and `latest`.

??? summary "max_players"
	### max_players

	:octicons-checklist-24: Type: `Number`
	{: .details }

	The maximum number of players that can be online for an update to be deemed nonintrusive.

??? summary "plugins"
	### plugins

	:octicons-checklist-24: Type: `Array`
	{: .details }

	An array of plugin names that this server uses. Plugin names must match those set in [`plugins.yaml`](../plugins) **exactly**. The names are case-sensitive.
