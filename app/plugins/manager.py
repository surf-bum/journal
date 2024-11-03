from app.plugins.tables import Plugin, PluginSerializer


class PluginManager:
    @classmethod
    async def create_plugin(cls, plugin):
        plugin = await Plugin.insert(
            Plugin(**plugin.dict()),
        ).returning(Plugin.name)
        plugin = plugin[0]

        return PluginSerializer(**plugin)

    @classmethod
    async def delete_plugin(cls, plugin_id) -> None:
        await Plugin.delete().where(Plugin.id == plugin_id)

    @classmethod
    async def get_plugin(cls, plugin_id) -> Plugin:
        return await Plugin.objects().get(Plugin.id == plugin_id)

    @classmethod
    async def get_plugins(cls) -> list:
        return await Plugin.select()
