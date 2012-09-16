class window.ChannellistView extends Backbone.View
    tagName: 'ul'
    className: 'nav nav-list'
    id: 'channelnavigation'

    initialize: -> 
        this.model.bind("all", ->
            this.render()
        , this)
    

    render: (eventName) ->
        $(this.el).children().remove()
        _.each(this.model.models, (channel) =>
            $(this.el).append(this.template(channel.toJSON()))
        )
        return this;
