var dsetModel = null;
var DatasetModel = ModelFactory(['currDataset'], []);
function init() {
    dsetModel = new DatasetModel({'currDataset':null});
    var dsetInfoView = new DatasetInfoView(dsetModel, $("dataset_focus"));
}

//NOTE: this MVC thing is making it more complicated than it needs, but 
//maybe this will pay off down the line?!
//NOTE: container is actually useless b/c makeHTML calls the fields directly
function DatasetInfoView(datasetModel, container) {
    this.datasetModel = datasetModel;
    this.container = container;

    var outer = this;

    this.currDatasetEventLstnr = function() { outer.makeHTML(); }
    this.datasetModel.currDatasetEvent.register(this.currDatasetEventLstnr);

    this.makeHTMLcb = function(req) {
	var dset = eval(req.responseText);
	var attrs = ['gsmid','name','species', 'factor', 'cell_line',  
		     'cell_type', 'cell_pop', 'strain', 'condition', 
		     'platform'];
	attrs.each(function(attr) {
		       if (dset[attr] != null) {
			   $('dset_'+attr).innerHTML = dset[attr];
		       }
		   });

	//handle file dnld link
	if (dset['file'] != null) {
	    //create an anchor tag
	}
    }

    this.makeHTML = function() {
	var currDset = outer.datasetModel.getCurrDataset();
	var getDataset = 
	new Ajax.Request(SUB_SITE+"jsrecord/Datasets/get/"+currDset+"/",
			 {method:"get", onSuccess: outer.makeHTMLcb});
    }

}

function setActiveDataset(dtsetId) {
    dsetModel.setCurrDataset(dtsetId);
}
