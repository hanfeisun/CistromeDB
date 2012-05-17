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
