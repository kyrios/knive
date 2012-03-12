console.log('Loading Viewport')
Ext.define('KN.view.Viewport', {
    extend: 'Ext.container.Viewport',
    layout: 'fit',
    items: [
    {
        xtype: 'panel',
        layout: 'border',
        items: [
        {
            xtype: 'panel',
            title: 'Knive - Cuts live',
            region: 'center',
            layout: 'fit',
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: [
                    { xtype: 'component', flex: 1 },
                    { xtype: 'button', text: 'New Show...', action: 'createShow', iconCls: 'add' },
                    { xtype: 'button', text: 'Settings...', action: 'openSettings', iconCls: 'settings' }
                ]
            },
            {
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: [{
                    xtype: 'component',
                    html: 'All systems up and running'
                },{
                    xtype: 'component',
                    flex: 1
                },{
                    xtype: 'button',
                    text: '',
                    iconCls: 'warning'
                }]
            }],
            items:[
            {
                xtype: 'showtabs',
            }]
        },
        {
            xtype: 'logconsole',
            title: 'Console',
            region: 'south',
            height: 100,
            split: true,
            collapsible: true,
            collapsed: true,
        }]
    }]
});
console.log('Loaded Viewport')
