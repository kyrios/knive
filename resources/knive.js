// Ext.require('Ext.container.Viewport');

Ext.application({
    name: 'KN',
    autoCreateViewport: true,
    appFolder: 'knive',
    controllers: [
                    'Main'
                ],
    
    launch: function() {
        console.log('Launched Knive');
    }
});