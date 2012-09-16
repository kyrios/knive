window.TopnavView = Backbone.View.extend
    initialize: ->
        @activeSection = 'Channels'

    render: ->
        $(this.el).html(this.template())
        $('#topnav' + @activeSection,this.el).addClass('active')
        return this

