/*
 * Utils.js
 *
 * Copyright (c) 2011 Len Taing
 *
 * Last Modified: Time-stamp: 
 *
 * Description:
 * A set of fns which I wished was included in prototype.js
 */

/**
 * Function: $D 
 * Description: dom element creator shortcut/convenience
 * var tmp = $D('span', {'class':'foo'});
 * RATHER than:
 * var tmp = document.createElement('span');
 * tmp.class = "foo";
 */
function $D(elmType, opts) {
    var tmp = document.createElement(elmType);
    if (opts) {
	//set optional fields
	for (var i in opts) {
	    tmp[i] = opts[i];
	}
    }

    return tmp;
}

/**
 * Function: getattr - my homage to the python fn
 * Description: dereferencing fn
 * @param: obj - javascript object
 * @param: field - string of the field to get
 * KEY note: this fn can follow dots., e.g. obj = {'foo':{'bar':5}}
 * getattr(obj, "foo.bar") --> 5
 */
function getattr(obj, field, debug) {
    var fldLst = field.split(".");
    var curr = obj;

    //just keep deref until we exhaust the list, or we break the link
    for (var i = 0; i < fldLst.length; i++) {
	//whenever we reach null, return
	if (curr == null) {
	    return null;
	}

	//otherwise, if we can't find the key
	var keys = Object.keys(curr);
	if (keys.indexOf(fldLst[i]) == -1) {
	    return null;
	} else {
	    curr = curr[fldLst[i]];
	}
    }
    return curr;
}

function inspect(obj) {
    var flds = "";
    for (x in obj) {
	flds += x + "\n";
    }
    return flds;
}

/**
 * shortens the string
 *
 * len - optional param specifying max length
 **/
function shorten(s, len) {
    if (s == null) { return "";}

    var max_length = (len) ? len : 30;
    if (s.length > max_length) {
	return s.substr(0, max_length - 3) + "...";
    } else {
	return s;
    }
}

/**
 * puts break tags </br> after every few words.  This is useful when
 * you have a long string and you need to display it broken up
 *
 * if s = Robertson G et al, Genome-wide profiles of STAT1 DNA association using chromatin immunoprecipitation and massively parallel sequencing. Nat. Methods . 2007
 * returns Robertson G et al, Genome-wide profiles of STAT1</br> DNA association using chromatin immunoprecipitation </br>and massively parallel sequencing. Nat. Methods . 2007
 *
 * k - number of words between breaks
 */
function insertBreaks(s, k) {
    var tmp = s.split(" ");
    var ret = "";
    for (var i = 0; i < tmp.length; i++) {
	ret += tmp[i] + " ";
	if (i != 0 && (i % k) == 0) {
	    ret += "</br>";
	}
    }
    return ret;
}

//ref: http://stackoverflow.com/questions/18082/validate-numbers-in-javascript-isnumeric
function IsNumeric(input) {
    return (input - 0) == input && input.length > 0;
}
