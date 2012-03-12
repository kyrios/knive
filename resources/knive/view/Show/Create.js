Ext.define('KN.view.Show.Create', {
    extend: 'Ext.window.Window',
    alias: 'widget.createShow',
    layout: 'fit',
    title: 'Create new Show',
    height: 300,
    width: 500,
    plain: false,
    modal: true,
    items: [{
    	xtype: 'panel',
    	html: 'Some content here...'
    }]
})