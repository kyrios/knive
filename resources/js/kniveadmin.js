var page = this;

var api = 'http://localhost:9001/apiV1';
$.read(
	'/apiV1/channel',
	function (response) {
		for (var i = response.channels.length - 1; i >= 0; i--) {
			$('#channelnavigation').append('<li class="nav-header">' + response.channels[i].name + '</li>');
			var broadcast = $('<li><a href="#">Broadcast</a></li>');
			broadcast.click({'channel': response.channels[i].slug},function (event) {
				viewChannelBroadcast(event);
			});
			$('#channelnavigation').append(broadcast);

			var settings = $('<li><a href="#">Settings</a></li>');
			$('#channelnavigation').append(settings);

			var episodes = $('<li><a href="#">Episodes</a></li>');
			episodes.click({'channel': response.channels[i].slug},function (event) {
				viewChannelEpisodes(event);
			});
			$('#channelnavigation').append(episodes);

			var statistics = $('<li><a href="#">Statistics</a></li>');
			$('#channelnavigation').append(statistics);
		}
	}
);

function viewChannelBroadcast (event) {
	$('#content').children().remove();
}

function viewChannelEpisodes (event) {
	$('#content').children().remove();
	var episodesdiv = $('<div class="row"><div class="span9 offset2"><table id="channeltable"><thead><tr><th>Name</th><th>Start Time</th><th>End Time</th></tr></thead></table></div></div>');
	$('#content').append(episodesdiv);
    $('#channeltable').dataTable( {
         "bProcessing": true,
         "sAjaxSource": '/apiV1/channel/tes/episode',
         "sAjaxDataProp": "episodes",
         "aoColumns": [
            { "mData": "name" },
            { "mData": "starttime" },
            { "mData": "endtime" }
        ]
    } );
}

