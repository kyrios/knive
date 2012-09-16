class window.SettingslistView extends Backbone.View
    console.log('SettingslistView loaded')
    tagName: 'ul'
    className: 'nav nav-list'
    id: 'settingsnavigation'

    initialize: -> 
        this.model.bind("all", ->
            this.render()
        , this)
    

    render: (eventName) ->
        $(this.el).html('')
        _.each(this.model.models, (setting) =>
            $(this.el).append(this.template(setting.toJSON()))
        )
        return this;
