//NOTE: this depends on FactorsTableView and FactorsInfoView which is in 
//home_factors.js.  So you must make sure that you include that file afore this

//NOTE: CellsTabModel is duplicate of FactorsTabModel
var CellsTabModel = ModelFactory(["factors", "cellsList", "models", "dsets", 
				  "currTd"], []);
var CellLines = loadJSRecord('CellLines');
var CellPops = loadJSRecord('CellPops');
var CellTypes = loadJSRecord('CellTypes');
var TissueTypes = loadJSRecord('TissueTypes');
var allCells = CellLines.all().concat(CellPops.all()).concat(CellTypes.all()).concat(TissueTypes.all());
allCells.sort(function(a,b){ 
	if (a.name == b.name) {
	    return 0;
	} else if (a.name > b.name) {
	    return 1;
	} else {
	    return -1;
	}});

var cellsModel = new CellsTabModel({'factors':null, 'cellsList':null, 
				    'models':null, 'dsets':null, 
				    'currTd':null});

var cells_msg = msg;

function init_cells() {
    var cellsListLstnr = function() {
	var list = cellsModel.getCellsList();
	var cellsSelect = $('cellsSelect');
	//CLEAR!
	cellsSelect.innerHTML = "";
	var map = {'CellLines':'cl', 'CellPops':'cp', 'CellTypes':'ct',
		   'TissueTypes':'tt'}
	for (var i = 0; i < list.length; i++) {
	    var type = (list[i].className)? map[list[i].className]:map[list[i]._class];

	    var tmp = $D('option',{'value':type+","+list[i].id, 
				'className': ((i % 2) == 0)? 'row':'altrow',
				'innerHTML':list[i].name});
	    cellsSelect.appendChild(tmp);
	}
    }
    cellsModel.cellsListEvent.register(function() {cellsListLstnr();});
    //init the select menu
    cellsModel.setCellsList(allCells);

    var cellsSearchCb = function(req) {
	var resp = eval("("+req.responseText+")");
	cellsModel.setCellsList(resp);

	//reset the search fld and search btn
	$('cells_searchBtn').disabled = false;
	$('cells_search').disabled = false;
	//$('factors_search').style.color = "#000";
	$('cells_search').className = "searchIn";
    }

    var cellsSearchURL = SUB_SITE + "search_cells";
    var cellsSearch = new SearchView($('cells_search'), 
				     $('cells_searchBtn'), 
				       cells_msg, cellsSearchURL, 
				       cellsSearchCb);


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

