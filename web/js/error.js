// error.js -- Gaff exception classes

function GaffException () {
    return new GaffException.fn.init ();
}

GaffException.fn = GaffException.prototype = {
    init: function () {
        this.$gaffException = true;
    },
    toString: function () {
        return 'GaffException';
    },
};
GaffException.fn.init.prototype = GaffException.fn;


// Some common errors

function ServiceNotReady (name) {
    // Data required for this service has not yet been loaded.
    this.serviceName = name;
}
ServiceNotReady.prototype = GaffException;

