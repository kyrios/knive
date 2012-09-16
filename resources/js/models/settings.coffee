class window.SettingsSection extends Backbone.RelationalModel
    urlRoot: '/apiV1/config'
    idAttribute: 'sectionName'
    relations:[
        type: Backbone.HasMany
        key: 'settings'
        relatedModel: 'window.Setting'
        collectionType: 'window.Settings'
    ]
    parse:(response) ->
        return response

window.SettingsSection.setup()

class window.Setting extends Backbone.RelationalModel
    idAttribute: 'key'
    relations:[
        type: Backbone.HasOne
        key: 'section'
        relatedModel: 'window.SettingsSection'
        collectionType: 'window.SettingsSections'
    ]

window.Setting.setup()


class window.Settings extends Backbone.Collection
    model: Setting


class window.SettingsSections extends Backbone.Collection
    model: SettingsSection
    url: 'apiV1/config'