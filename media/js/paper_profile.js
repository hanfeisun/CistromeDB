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
	var dset = eval("("+req.responseText+")");
	//alert(req.responseText);
	//these are strings
	var attrs = ['gsmid','name']
	//these are records, we want to print the names
	var attrs_rec = ['species', 'factor', 'cell_type', 'cell_pop',
			 'strain', 'condition', 'platform']
	attrs.each(function(attr) {
		       if (dset[attr] != null) {
			   $('dset_'+attr).innerHTML = dset[attr];
		       }
		   });
	attrs_rec.each(function(attr) {
			   if (dset[attr] != null) {
			       var val = dset[attr].name;
			       if (val.length >= 13) {
				   //NOTE: w/o the g only the first space 
				   //will be replaced!
				   val = val.replace(/\s+/g, "</br>");
				   /* GOOD but not perfect--want to chunk by 
				      size 13
				   //try to split it in half
				   var i = val.indexOf(" ", val.length/2);
				   if (i >= 0) {
				       val = val.substring(0,i) + "</br>"+
					   val.substring(i, val.length);
				   } else {
				       val = val.substring(0,13) + "...";
				   }
				   */
			       }
			       $('dset_'+attr).innerHTML = val;
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
