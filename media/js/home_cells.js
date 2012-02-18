//NOTE: this depends on FactorsTableView and FactorsInfoView which is in 
//home_factors.js.  So you must make sure that you include that file afore this

//NOTE: CellsTabModel is duplicate of FactorsTabModel
var CellsTabModel = ModelFactory(["factors", "cellsList", "models", "dsets", 
				  "currTd"], []);
var cellsModel = new CellsTabModel({'factors':null, 'cellsList':null, 
				    'models':null, 'dsets':null, 
				    'currTd':null});
var allCells = [];
var cells_msg = msg;

var drawCellsSelect = function(list) {
    var cellsSelect = $('cellsSelect');
    //CLEAR!
    cellsSelect.innerHTML = "";
    var map = {'CellLines':'cl', 'CellPops':'cp', 'CellTypes':'ct',
	       'TissueTypes':'tt'}
    for (var i = 0; i < list.length; i++) {
	var type = map[list[i]._class];
	var tmp = $D('option',{'value':type+","+list[i].id, 
			       'className': ((i % 2) == 0)? 'row':'altrow',
			       'innerHTML':list[i].name});
	cellsSelect.appendChild(tmp);
    }
}
function init_cells() {
    var cellsListLstnr = function() {
	var list = cellsModel.getCellsList();
	drawCellsSelect(list);
    }
    var jumpView= new JumpView($('cells_jump'), "getCellsList", 
			       drawCellsSelect, "cells");
    cellsModel.cellsListEvent.register(function() {cellsListLstnr();});
    cellsModel.cellsListEvent.register(jumpView.listener);

    //init the select menu
    //take the initial list and save it into allCells
    var cs = $('cellsSelect');
    allCells = [];
    var revMap = {'cl':'CellLines', 'cp':'CellPops', 'ct':'CellTypes',
		  'tt':'TissueTypes'};
    for (var i = 0; i < cs.options.length; i++) {
	var j = cs.options[i].value.indexOf(",");
	var mod = cs.options[i].value.substr(0, j);
	var id = cs.options[i].value.substr(j+1, cs.options[i].value.length);
	var name = cs.options[i].innerHTML;
	var tmp = {"_class":revMap[mod], "id":id, "name":name}
	allCells.push(tmp);
    }    

    var cellsSearchCb = function(req) {
	var resp = eval("("+req.responseText+")");
	cellsModel.setCellsList(resp);

	$('cells_cancelBtn').style.display="inline";
    }
    //trigger the jumpView
    cellsModel.setCellsList(allCells);


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

    //set the action for the cancelBtn
    var cancelBtn = $('cells_cancelBtn');
    cancelBtn.onclick = function(event) {
	cellsModel.setCellsList(allCells);
	//reset the search fld and search btn
	$('cells_searchBtn').disabled = false;
	$('cells_search').disabled = false;
	$('cells_search').value = "";
	$('cells_search').className = "searchIn";
	cancelBtn.style.display="none";
	//HACK: to get the msg displayed, set the focus on the search, then 
	//move it to the select
	$('cells_search').focus();
	$('cellsSelect').focus();
    }

}

