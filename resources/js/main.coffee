window.KniveRouter = Backbone.Router.extend 

    routes:
        "" : "channels"
        "channels": "channels"
        "channels/:channel": "channels"
        "settings": "settings"
        "console": "console"

    channels: (channel)->
        console.log("Channel #{channel} active")
        if !this.topnavView
            this.topnavView = new TopnavView()
            $("#topnav").html(this.topnavView.el)
        this.topnavView.activeSection = 'Channels'
        this.topnavView.render()
        

        if !this.sidenavView
            this.sidenavView = new SidenavView()
            this.sidenavView.render()
        $("#sidenav").html(this.sidenavView.el)

        this.channellist = new Channels()
        this.channellist.fetch()
        if !this.channellistView
            this.channellistView = new ChannellistView(model:this.channellist)
            $(this.sidenavView.el).html(this.channellistView.el)
        
        

    settings: ->
        console.log('Settings active')
        if !this.topnavView
            this.topnavView = new TopnavView()
            $("#topnav").html(this.topnavView.el);
        this.topnavView.activeSection = 'Settings'
        this.topnavView.render()
        
        if !this.sidenavViewSettings
            this.sidenavViewSettings = new SidenavView()
            this.sidenavViewSettings.render()
        $("#sidenav").html(this.sidenavViewSettings.el)

        this.settingsSections = new SettingsSections()
        this.settingsSections.fetch()

        if ! this.settingslistView 
            this.settingslistView = new SettingslistView(model:this.settingsSections)
        $(this.sidenavViewSettings.el).html(this.settingslistView.el)

views = [
    "TopnavView"
    "SidenavView"
    "ChannellistView"
    "ChannellistitemView"
    "SettingslistView"
    ]

templateLoader.load views, ->
    window.app = new KniveRouter()
    Backbone.history.start()