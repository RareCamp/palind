"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DateSanitizer = exports.GenderSanitizer = exports.StringSanitizer = void 0;
var StringSanitizer = /** @class */ (function () {
    function StringSanitizer() {
    }
    StringSanitizer.prototype.sanitize = function (field) {
        field = field.toLowerCase();
        field = field.trim();
        field = field.replace(/\s/g, ' ');
        field = field.replace(/  +/g, ' ');
        return field;
    };
    return StringSanitizer;
}());
exports.StringSanitizer = StringSanitizer;
var GenderSanitizer = /** @class */ (function () {
    function GenderSanitizer() {
    }
    GenderSanitizer.prototype.sanitize = function (gender) {
        var stringSanitizer = new StringSanitizer();
        gender = stringSanitizer.sanitize(gender);
        var MALE = ["m", "male", "man", "boy"];
        var FEMALE = ["f", "female", "woman", "girl"];
        if (MALE.includes(gender)) {
            return "M";
        }
        if (FEMALE.includes(gender)) {
            return "F";
        }
        throw Error("Unknown gender: " + gender);
    };
    return GenderSanitizer;
}());
exports.GenderSanitizer = GenderSanitizer;
var DateSanitizer = /** @class */ (function () {
    function DateSanitizer() {
    }
    DateSanitizer.prototype.sanitize = function (date) {
        return date;
    };
    return DateSanitizer;
}());
exports.DateSanitizer = DateSanitizer;
