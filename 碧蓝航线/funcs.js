
Array.prototype.contains = function (obj) {
    var i = this.length;
    while (i--) {
        if (this[i] === obj) {
            return true;
        }
    }
    return false;
}

String.prototype.format = function () {
    if (arguments.length === 1 && typeof (arguments[0]) === "object") {
        var args = arguments[0];
    } else {
        var args = arguments;
    }
    console.log(arguments);
    console.log(args);
    return this.replace(/\{(.+?)\}/g, function (full, key) {
        return typeof (args[key]) === "undefined" ? key : args[key];
    });
}
