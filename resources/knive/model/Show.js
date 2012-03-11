Ext.define('KN.model.Show', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'id',  type: 'integer'},
        {name: 'name',  type: 'string'},
        {name: 'slug',  type: 'string'},
        {name: 'url', type: 'string'},
    ],
    proxy: {
         type: 'rest',
         url  : '/data/channel',
         reader: {
             root: 'channels'
         }
    }
});