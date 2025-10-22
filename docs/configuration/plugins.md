# Plugins

The plugins configuration file, [`config/plugins.yaml`](https://github.com/Left4Craft/spigot-updater/blob/master/config/plugins.yaml).
This file should contain a YAML structure of plugin objects:

=== "Spigot"
    ```yaml
    PluginName:
      source: 'spigot'
      resource: 12345
      zip_path: 'optional-file.jar'  # optional, String or RegEx
      jar: 'PluginName.jar'
    ```

=== "GitHub"
    ```yaml
    PluginName:
      source: 'github'
      repo: 'owner/repository'
      asset: 'plugin.jar'  # String or RegEx
      zip_path: 'optional-file.jar'  # optional, String or RegEx
      jar: 'PluginName.jar'
    ```

=== "Jenkins"
    ```yaml
    PluginName:
      source: 'jenkins'
      host: 'https://ci.example.com'
      job: 'JobName'
      artifact: 'artifact.jar'  # String or RegEx
      zip_path: 'optional-file.jar'  # optional, String or RegEx
      jar: 'PluginName.jar'
    ```

## Plugin properties

??? summary "source"
	### source

	:octicons-file-symlink-file-24: Required
	{: .details }

	:octicons-list-unordered-24: Sources: `spigot`, `github`, `jenkins`
	{: .details }

	:octicons-checklist-24: Type: `String`
	{: .details }

	The source of the plugin - one of:

	- `spigot`
	- `github`
	- `jenkins`

??? summary "jar"
	### jar

	:octicons-file-symlink-file-24: Required
	{: .details }

	:octicons-list-unordered-24: Sources: `spigot`, `github`, `jenkins`
	{: .details }

	:octicons-checklist-24: Type: `String`
	{: .details }

	The filename of the file on the server, like `EssentialsX.jar`.

??? summary "zip_path"
	### zip_path

	:octicons-info-24: Optional
	{: .details }

	:octicons-list-unordered-24: Sources: `spigot`, `github`, `jenkins`
	{: .details }

	:octicons-checklist-24: Type: `String` or `RegEx`
	{: .details }

	The name and location of the file to extract if the plugin download in compressed/zipped.

	If you know the exact file name, set this to a string (`'Filename.jar'`). If the file name changes every time, use regex (`'BungeeTabListPlus_BukkitBridge-\S*\.jar'`).

??? summary "resource"
	### resource

	:octicons-file-symlink-file-24: Required
	{: .details }

	:octicons-list-unordered-24: Sources: `spigot`
	{: .details }

	:octicons-checklist-24: Type: `Number`
	{: .details }

	The spigot resource ID. This is the number at the end of the URLs: `https://www.spigotmc.org/resources/essentialsx.9089` :octicons-arrow-right-24: `9089`.

??? summary "repository"
	### repo

	:octicons-file-symlink-file-24: Required
	{: .details }

	:octicons-list-unordered-24: Sources: `github`
	{: .details }

	:octicons-checklist-24: Type: `String`
	{: .details }

	The GitHub repository of the plugin - `org/repo` or `user/repo`.

	**Note**: This was previously called `repository` in older versions.

??? summary "asset"
	### asset

	:octicons-file-symlink-file-24: Required
	{: .details }

	:octicons-list-unordered-24: Sources: `github`
	{: .details }

	:octicons-checklist-24: Type: `String` or `RegEx`
	{: .details }

	The name of the asset to download. If the name of the asset is different every time, you can either use RegEx, or if the name is predictable and included the tag name, you can use the `{{tag}}` placeholder.

??? summary "host"
	### host

	:octicons-file-symlink-file-24: Required
	{: .details }

	:octicons-list-unordered-24: Sources: `jenkins`
	{: .details }

	:octicons-checklist-24: Type: `String`
	{: .details }

	The web address for jenkins instance, like `https://ci.example.net`.

??? summary "job"
	### job

	:octicons-file-symlink-file-24: Required
	{: .details }

	:octicons-list-unordered-24: Sources: `jenkins`
	{: .details }

	:octicons-checklist-24: Type: `String`
	{: .details }

	The name of the CI job.

??? summary "artifact"
	### artifact

	:octicons-file-symlink-file-24: Required
	{: .details }

	:octicons-list-unordered-24: Sources: `jenkins`
	{: .details }

	:octicons-checklist-24: Type: `String` or `RegEx`
	{: .details }

	The name of the artifact to download. If the name of the artifact is different every time, you can either use RegEx, or if the name is predictable and included the build number, you can use the `{{build}}` placeholder.
