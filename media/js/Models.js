/*
 * Models.js
 *
 * Copyright (c) 2007 Len Taing
 *
 * Last Modified: Time-stamp: <2010-12-28 17:38:26 lentaing>
 *
 * Description:
 * Model classes hold all of the data that a page requires.  The data is 
 * accessed through "getter" functions, e.g. Foo.getName().  The data is 
 * updated through "setter" functions, e.g. Foo.setName("bob").  When the data
 * changes, the model notifies its listeners of the update.  These listeners
 * are usually "Views" that may refresh themselves based on the changes in the
 * data model.
 *
 * ModelEvent is the class that handles all of the model event notifications.
 *
 */

/**
 * Class: ModelEvent
 * Description: This class does two important things: 1. register listeners
 * for a model event, and 2. when the model event is "invoked" (via the 
 * notify method), all of the registered listeners are informed.
 *
 * @param: modelRef -- the object that is passed as the message of notify
 * NOTE: it is customary for modelRef to be MODEL that uses the Model Event
 */
function ModelEvent(modelRef) {
    this.modelRef = modelRef;
    this.listeners = [];
    var outer = this;
    
    this.register = function(listenerFn) {
	var i = outer.listeners.indexOf(listenerFn);
	//make sure there are no duplicates
	if (i == -1) { outer.listeners.push(listenerFn);}
    }
    
    this.unregister = function(listenerFn) {
	var i = outer.listeners.indexOf(listenerFn);
	if (i != -1) { outer.listeners.splice(i, 1);}
    }
    
    this.notify = function() {
	outer.listeners.each(function(lstnr) {lstnr(outer.modelRef);});
    }
}

/**
 * Class: ModelFactory
 * Description: This Class Factory generates Model classes.  Model classes 
 * have three responsibilities: 1. store data, 2. have set/get fns to access 
 * the data, and 3. have ModelEvents that are invoked when the data changes
 *
 * This factory takes two arrays as arguments: getsetters are fields that we 
 * we want define getter AND setter functions for (they are the "read/write"
 * fields).  They also have associated ModelEvents--when the setter function
 * changes the field's value, the event is invoked.
 *
 * getters are "readonly" i.e. they only have associated "getter" fns.
 *
 * NOTE: field names MUST follow java variable name conventions: firstword
 * lowercase, every other word after is upper-cased.
 *
 * generates methods like: (assuming the field is called "firstField") 
 * getFirstField, setFirstField, firstFieldEvent.
 *
 * The factory returns a CLASS that expects one argument: an object that 
 * associates each field name w/ a the given value, e.g. {foo:5, bar:true},
 * OR EntryModel(entryId, placeId,...) --> EntryModel({entryId:,placeId:});
 *
 * @param getsetters - instance vars we want to be read&writable
 * @param getters - instance vars we want to be readonly
 * @return a new ModelClass
 *
 */
function ModelFactory(getsetters, getters) {
    return function(paramObj) {
	var outer = this;
	this.fields = getsetters.concat(getters);
	
	//create the getter functions
	for (var i = 0; i < getters.length; i++) {
	    this[getters[i]] = paramObj[getters[i]];
	    var name = upperCase1stLtr(getters[i]);
	    //we need a closure to grab the REF to the field value
	    this["get"+name] = function(field) { 
		return function(){ return outer[field]; }
	    }(getters[i]);

	}

	//set the incoming params: e.g. this.entryId = paramObj.entryId
	//and create get functions
	for (var i = 0; i < getsetters.length; i++) {
	    this[getsetters[i]] = paramObj[getsetters[i]];
	    var name = upperCase1stLtr(getsetters[i]);
	    //Again we need a closure for help
	    this["get"+name] = function(field) {
		return function(){return outer[field]; }
	    }(getsetters[i]);
	    
	    //create the event and set functions
	    this[getsetters[i]+"Event"] = new ModelEvent(this);
	    this["set"+name] = function(field) {
		return function(param) {
		    //ALWAYS NOTIFY
		    //if (param != outer[field]) {
			outer[field] = param;
			outer[field+"Event"].notify();
			//}
		}
	    }(getsetters[i])
	}
    }
}

/**
 * Fn: takes a string and returns the string w/ the first letter uppercased
 * NOTE: maybe I should move the following to a file called StringUtils.
 */
function upperCase1stLtr(s) {
    if (s == null) { return null;}
    if (s.length > 0) {
	var ltr = s.substring(0,1);
	var rest = s.substring(1,s.length);
	return ltr.toUpperCase() + rest;
    } else {//empty string
	return "";
    }
}

/**
 * Class: JSRecordFactory
 * Description: These are the model objects for JSRecord.  They sub-class the 
 * model factory, so all of the basic model things (e.g. events and 
 * get/setters) are inherited, but they also allow for direct DB manipulation 
 * via (jsrecord) ajax calls.  These functions are like the ones found in 
 * Django or Ruby on rails models, e.g.
 * 
 * Series is a JSRecord model class.  You can do things like: Series.get,
 * Series.all; s is an instance of Series.  you can do things like: s.save,
 * s.delete, s = new Series(...)
 *
 * Class Methods: 
 * all - get all of the model objects of that type from the db
 * get - given an id, will try to retrieve the object in the db w/ the id
 * deserialize (json)- try to deserialize the json and create a new instance
 * of the class
 *
 * Instance Methods:
 * save- save the current object to the db; if the object already exists, 
 * update the row
 * delete- delete the object from the db
 * serialize - conver this object into json
 *
 * @param: fields- array of field names that the JSRecord class will hold
 * NOTE: these will all be passed in as "getsetters"
 */
//NOTE: we are dropping this for SUB_SITE which is defined in settings.js
//var PREFIX_URL = "/modENCODE";

function JSRecordFactory(className, fields) {
    var tmpClass = function(paramObj) {
	this.superclass = ModelFactory(fields, []);
	this.superclass(paramObj);

	var outer = this;
	//NOTE: this is duplicated!--should just be classfields!
	this.jsrecordURL = SUB_SITE+"jsrecord/";
	this.className = className;


	//INSTANCE METHODS!
	this.save = function(callbackFn) {
	    var save = 
	    new Ajax.Request(outer.jsrecordURL+outer.className+"/save/", 
			     {method:"post", onComplete: callbackFn, 
			      parameters: eval("("+outer.serialize()+")")});
	}
	
	this.deleteThis = function(callbackFn) {
	    if (outer.id != null) {
		var deleteCall = 
		new Ajax.Request(outer.jsrecordURL+outer.className+"/delete/"+
				 outer.id+"/",
				 {method:"get", onComplete: callbackFn});
	    } else { //TRYING to delete an object in the DB that is null
		var req = {}
		req.responseText = "({success:false})"
		cbFn(req);
	    }
	}
   
	//RETURNS a string representing this record object
	//overriding what we get from OBJECT
	this.toJSON = function () {
	    json = "";
	    if (outer.fields.length > 0) {
		var val = outer[outer.fields[0]];
		json += outer.fields[0]+":"+
		    (typeof val == 'string'?"\""+val+"\"":val)
	    }
	    for (i = 1; i < outer.fields.length; i++) {
		var val = outer[outer.fields[i]];
		json += ", "+outer.fields[i]+":"+
		(typeof val == 'string'?"\""+val+"\"":val)
	    }
	    return "{"+json+"}";
	}

	this.serialize = function() {
	    return outer.toJSON();
	}
    }

    //NOTE: these are the fields in the django model--its also in instances
    tmpClass.fields = fields;

    //adding class methods
    tmpClass.jsrecordURL = SUB_SITE+"jsrecord/";
    tmpClass.className = className;

    tmpClass.all = function() {
	this.returnVal = null;
	var outer = this;   
	
	//expects return to be: [S1, S2, ..., SN]
	this.callback = function(req) {
	    resp = eval(req.responseText);
	    var tmp = [];
	    for (var i = 0; i < resp.size(); i++) {
		var s = outer.deserialize(resp[i]);
		tmp.push(s);
	    }
	    outer.returnVal = tmp;
	}
	
	var getAll = 
	new Ajax.Request(outer.jsrecordURL+outer.className+"/all/", 
			 {method:"get", onSuccess: outer.callback, 
				 asynchronous:false});
	
	return this.returnVal;
    }


    tmpClass.get = function(pk) {
	this.returnVal = null;
	var outer = this;
	
	this.callback = function(req) {
	    resp = eval(req.responseText);
	    outer.returnVal = outer.deserialize(resp);
	}
	
	//NOTE/WARNING: we are making a serialized ajax call--its not rec. but
	//this is the only way i can get it to block
	var get = 
	new Ajax.Request(outer.jsrecordURL+outer.className+"/get/"+pk+"/", 
			 {method:"get", onSuccess: outer.callback, 
				 asynchronous:false});
	
	return this.returnVal;
    }

    tmpClass.find = function(options) {
	this.returnVal = null;
	var outer = this;
	
	this.callback = function(req) {
	    resp = eval(req.responseText);
	    var tmp = [];
	    for (var i = 0; i < resp.size(); i++) {
		var s = outer.deserialize(resp[i]);
		tmp.push(s);
	    }
	    outer.returnVal = tmp;
	}
	
	//NOTE/WARNING: we are making a serialized ajax call--its not rec. but
	//this is the only way i can get it to block
	var get = 
	new Ajax.Request(outer.jsrecordURL+outer.className+"/find/",
			 {method:"get", onSuccess: outer.callback, 
				 parameters:options, asynchronous:false});
	
	return this.returnVal;
    }

    tmpClass.deserialize = function(json) {
	var tmp = new this(json); //COOL! i didn't know that you could do that
	return tmp;
    }


    return tmpClass;
}

/**
 * Function: loadJSRecord
 * Description: This function makes an ajax call to jsrecord to dynamically 
 * "import" the record into javascript land
 *
 * @params- model name
 */
loadJSRecord = function(model) {
    this.returnVal = null;
    var outer = this;
    
    this.callback = function(req) {
	resp = eval(req.responseText);
	outer.returnVal = JSRecordFactory(resp.className, resp.fields);
    }
    
    //NOTE/WARNING: we are making a serialized ajax call--its not rec. but
    //this is the only way i can get it to block
    var getSeries = 
    new Ajax.Request(SUB_SITE+"jsrecord/load/"+model+"/", 
		     {method:"get", onSuccess: outer.callback, 
			     asynchronous:false});
    
    return this.returnVal;
}
