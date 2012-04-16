Ext.define('KN.controller.Main', {
    extend: 'Ext.app.Controller',
    views: [
                'Logconsole',
                'Settings',
                'ShowTabs',
                'Show.Create',
                'Show.Overview'
    ],
    stores: [
                'Show'
    ],
    refs: [{
        ref: 'createShow',
        selector: 'createShow',
        forceCreate: true,
        xtype: 'showCreate',
    },
    {
        ref: 'openSettings',
        selector: 'settings',
        autoCreate: true,
        xtype: 'settings',
        
    }],

    init: function() {
        console.log('Initialized Main Controller');
        var self = this
        
        this.control({
            'showtabs': {
                render: this.onShowTabsAvailable
            },
            'button[action=createShow]': {
                click: this.onCreateShowTap
            },
            'button[action=openSettings]': {
                click: this.onOpenSettingsTap
            }
            
        })
    },
    addNewShow: function(show,showTab){
        var self = this
        console.log('Adding show ' + show)
        var showController = Ext.create('KN.controller.Show',{
            showName: show,
        })
        showController.init()
        var showView = Ext.create('KN.view.Show.Overview')
        showView.title = show
        showTab.add(showView)
    },

    onShowTabsAvailable: function(showTab) {
        var self = this
        console.log('Loading Shows')
        var showStore = this.getShowStore()
        showStore.load(function(showRecords){
            showStore.each(function(show){
                console.log('Loaded show '+ show.get('name'))
                self.addNewShow(show.get('name'),showTab)

            })
        })
    },
    onCreateShowTap: function () {
        this.getCreateShow().show()
    },
    onOpenSettingsTap: function () {
        this.getOpenSettings().show()
    }
});
console.log('Loaded main Controller')