Ext.define('KN.view.Show', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.show',
    layout: 'border',
    items: [
    {
    	xtype: 'panel',
    	region: 'center',
        html: 'Some content here'
    },
    // {
    // 	xtype: 'showNavigation',
    //     store: Ext.create('KN.store.Show.Navigation',{})
    // }
    ]
})