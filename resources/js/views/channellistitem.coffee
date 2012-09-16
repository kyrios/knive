class window.ChannellistitemView extends Backbone.View
    render: ->
        $(this.el).html(this.template())
        return this