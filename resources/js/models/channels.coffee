class window.Channel extends Backbone.Model

class window.Channels extends Backbone.Collection
    model: Channel
    url: "apiV1/channel"

    # parse: (response) ->
    # 	# console.log('Parsing Channels')
    # 	return response.channels