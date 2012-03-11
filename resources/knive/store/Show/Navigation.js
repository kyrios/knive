console.log('Loading Show Navigation Store');

Ext.define('KN.store.Show.Navigation', {
    extend: 'Ext.data.TreeStore',
    root: {
        expanded: true,
        children: [
            {
                text: 'Overview',
                leaf: true
            }, 
            {
                text: 'Settings',
                leaf: true,
            },
            {
                text: 'Inlet',
                leaf: true
            }, 
            {
                text: 'Outlets',
                leaf: false,
                childen: [
                {
                    text: 'FileWriter',
                    leaf: true,
                },
                {
                    text: 'HTTP Live Streamer',
                    leaf: false,
                    children:[{
                        text: 'Settings',
                        leaf: 'true'
                    },
                    {
                        text: 'Qualities',
                        leaf: false,
                        children: [{
                            text: 'WiFi',
                            leaf: true,
                        },
                        {
                            text: 'HSDPA',
                            leaf: true,
                        },
                        {
                            text: 'EDGE',
                            leaf: true,
                        },
                        {
                            text: 'Audio 64kBit/s',
                            leaf: true,
                        }]
                    }]
                },
                {
                    text: 'IceCast2',
                    leaf: true
                }]
            },
            {
                text: 'Statistics',
                leaf: true
            }, 
            {
                text: 'Episodes',
                leaf: true
            }, 
        ]
    }
});
console.log('Loaded Show Navigation Store');
