/**
 * This file contains the data models, viewers, and controllers for the 
 * paper's page.
 *
 * Models: 
 *   PapersModel: the papers list, the current paper
 * Views: 
 *   Given a PapersModel, construct the table of papers
 *   Given a CurrentPaper, construct the info and datasets section
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
	 for (var i = 0; i < outer.listeners.length; i++) {
	     outer.listeners[i](outer.modelRef);
	 }
     }
}

/**
 * CLASS: PapersModel
 * Description: This model contains a list of all of the papers, and the 
 * current paper selected
 */
function PapersModel(papersList) {
    this.papersList = papersList;
    this.currentPaperID = null;
    var outer = this;
    
    this.papersListEvent = new ModelEvent(this);
    this.currentPaperIDEvent = new ModelEvent(this);
    
    this.setCurrentPaperID = function(id) {
	if (outer.currentPaperID != id){
	    outer.currentPaperID = id;
	}
	outer.currentPaperIDEvent.notify()
    }

    this.getPaper = function(index) {
	if (index >= 0 && index < outer.papersList.length) {
	    return outer.papersList[index];
	} else {
	    return null;
	}
    }
    
    this.getCurrPaper = function() {
	if (outer.currentPaperID == null) {
	    return null;
	} else {
	    return outer.getPaper(outer.currentPaperID);
	}
    }
}

/**
 * constructs the paper info view
 */
function PaperInfoView(papersModel, container) {
    this.papersModel = papersModel;
    this.container = container;
    var outer = this;

    this.currPaperLstnr = function() {
	outer.draw();
    }
    outer.papersModel.currentPaperIDEvent.register(outer.currPaperLstnr);

    this.draw = function() {
	var currPaper = outer.papersModel.getCurrPaper();
	if (currPaper != null) {
	    var fields = ['title', 'authors', 'abstract'];
	    var newTable = document.createElement('table');
	    for (var i = 0; i < fields.length; i++) {
		var newTR = document.createElement('tr');
		var label = document.createElement('td');
		label.innerHTML = fields[i]+":";
		label.className = "fld_label";
		newTR.appendChild(label);
		
		var val = document.createElement('td');
		val.innerHTML = currPaper[fields[i]];
		val.className = "fld_value";
		newTR.appendChild(val);
		newTable.appendChild(newTR);
	    }
	    if (outer.container.childNodes.length > 0) {
		outer.container.replaceChild(newTable,
					     outer.container.childNodes[0]);
	    } else {
		outer.container.appendChild(newTable);
	    }
	}
    }
}

/**
 * constructs the dataset info view
 */
function DatasetsInfoView(papersModel, container) {
    this.papersModel = papersModel;
    this.container = container;
    var outer = this;
    this.datasetList = null;
    
    this.currPaperLstnr = function() {
	outer.getDatasetList(outer.papersModel.getCurrPaper());
    }
    outer.papersModel.currentPaperIDEvent.register(outer.currPaperLstnr);

    this.datasetListEvent = new ModelEvent(this);
    this.setDatasetList = function(dlist) {
	outer.datasetList = dlist;
	outer.datasetListEvent.notify();
    }
    //NOTE: given a PAPER, retrieve the datasets associated with that PAPER
    //through AJAX and then set it.
    this.getDatasetList = function(currPaper) {
	var url = "/get_datasets/"+currPaper.id+"/";
	var getDataset = 
	new Ajax.Request(url, {onComplete:outer.getDatasetListCb});
    }
    this.getDatasetListCb = function(req) {
	var dlist = eval("("+req.responseText+")");
	outer.setDatasetList(dlist);
    }
    
    this.draw = function() {
	if (outer.datasetList != null) {
	    //missing other info
	    var fields = ["gsmid", "platform", "exp_type", "species", "factor",
			  "cell_type", "file"];
	    var newTable = document.createElement('table');
	    var newTR = document.createElement('tr');
	    newTable.appendChild(newTR);
	    //create the header
	    for (var i = 0; i < fields.length; i++) {
		var newTH = document.createElement('th');
		newTH.innerHTML = fields[i];
		newTR.appendChild(newTH);
	    }
	    //fill in data
	    for (var i = 0; i < outer.datasetList.length; i++) {
		newTR = document.createElement('tr');
		newTable.appendChild(newTR)
		for (var j = 0; j < fields.length; j++) {
		    var newTD = document.createElement('td');
		    if (fields[j] == "file") {
			var newA = document.createElement('a');
			newA.href = outer.datasetList[i]['file'];
			newA.innerHTML = "download";
			newTD.appendChild(newA);
		    } else {
			newTD.innerHTML = outer.datasetList[i][fields[j]];
		    }
		    newTR.appendChild(newTD);
		}
	    }
	    if (outer.container.childNodes.length > 0) {
		outer.container.replaceChild(newTable,
					     outer.container.childNodes[0]);
	    } else {
		outer.container.appendChild(newTable);
	    }
	}
    }
    this.datasetListEvent.register(outer.draw);
}

var papersModel;
var paperInfoView;
var datasetsContainer;
function initPage(papersList) {
    papersModel = new PapersModel(papersList);
    var infoContainer = document.getElementById('info_container');
    var datasetsContainer = document.getElementById('dataset_container');
    paperInfoView = new PaperInfoView(papersModel, infoContainer);
    datasetsInfoView = new DatasetsInfoView(papersModel, datasetsContainer);
}

