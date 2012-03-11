Ext.define('KN.view.Settings', {
    extend: 'Ext.window.Window',
    alias: 'widget.settings',
    layout: 'fit',
    title: 'Global Settings',
    height: 300,
    width: 500,
    plain: true,
    modal: true,
    items: [{
    	xtype: 'panel',
    	html: 'Some settings here...'
    }]
})