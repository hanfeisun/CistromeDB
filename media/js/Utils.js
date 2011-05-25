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

