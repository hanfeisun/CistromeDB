//NOTE: this depends on FactorsTableView and FactorsInfoView which is in 
//home_factors.js.  So you must make sure that you include that file afore this

//NOTE: CellsTabModel is duplicate of FactorsTabModel
var CellsTabModel = ModelFactory(["factors", "models", "dsets", "currTd"], []);
var cellsModel = new CellsTabModel({'factors':null, 'models':null, 
				    'dsets':null, 'currTd':null});


function init_cells() {
    var cellsFactorsTableView = 
	new FactorsTableView($('cellsFactorsTable'), cellsModel, true);
    var cellsFactorInfoView = 
	new FactorInfoView($('cellsFactorInfo'), cellsModel);
    cellsModel.dsetsEvent.register(function() { cellsFactorsTableView.makeHTML();});
    cellsModel.currTdEvent.register(function() { cellsFactorInfoView.makeHTML();});

    var cellsDrawBtn = $('cellsDrawBtn');
    cellsDrawBtn.onclick = function(event) {
	this.disabled = true;
	var cells = [];
	var cs = $('cellsSelect');
	for (var i = 0; i < cs.options.length; i++) {
	    if (cs.options[i].selected) {
		cells.push(cs.options[i].value);
	    }
	}
	
	//LIMIT 1
	var cStr = (cells.length > 0) ? cells[0]:"";

	var cells_view_cb = function(req) {
	    cellsDrawBtn.disabled = false;
	    var resp = eval("("+req.responseText+")");
	    cellsModel.setFactors(resp.factors);
	    cellsModel.setModels(resp.models);
	    cellsModel.setDsets(resp.dsets);
	    //CLEAR the factorInfoView
	    cellsFactorInfoView.clearHTML();
	}
	//MAKE the ajax call-
	var call = new Ajax.Request(SUB_SITE+"cells_view/", 
    {method:"get", parameters: {'cells':cStr}, 
     onComplete: cells_view_cb});

    }
}

