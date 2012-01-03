var cutoff = 0.015;
var topCut = 20;

function prepareData(d) {
    var total = 0;
    for (var i = 0; i < d.length; i++) {
	total += d[i].count;
    }

    var foo = [];
    var other = 0;
    for (var i = 0; i < d.length; i++) {
	var per = d[i].count / total;
	if (per > cutoff) {
	    foo.push([d[i].label, Math.round(per*10000)/100]);
	} else {
	    other += d[i].count;
	}
    }
    if (other > 0) {
	foo.push(['other', Math.round(other/total*10000)/100]);
    }
    return foo;
}

function prepareBarData(d) {
    var categories = [];
    var vals = [];
    for (var i = 0; i < d.length; i++) {
	categories.push(d[i].label);
	vals.push(d[i].count);
    }
    return {categories:categories, values:vals};
	
}

function pieChartFactory(container, title, data) {
    var chart = new Highcharts.Chart({
	    chart: {
		renderTo: container,
		    plotBackgroundColor: null,
		    plotBorderWidth: null,
		    plotShadow: false
		    },
		title: {
		text: title
		    },
		tooltip: {
		formatter: function() {
		    return '<b>'+ this.point.name +'</b>: '+ this.y +' %';
		}
	    },
		plotOptions: {
		pie: {
		    allowPointSelect: true,
			cursor: 'pointer',
			dataLabels: {
			enabled: true,
			    color: '#000000',
			    connectorColor: '#000000',
			    formatter: function() {
			    return '<b>'+ this.point.name +'</b>: '+ this.y +' %';
			}
		    }
		}
	    },
		series: [{type:'pie',
		    name: title, 
		    data: data}]
		});
}

function barChartFactory(container, title, data) {
    //data: {categories:['foo','bar'],values[21, 22]}

    var chart = new Highcharts.Chart({
	    chart: {
		renderTo: container,
		    defaultSeriesType: 'column',
		    margin: [ 50, 50, 100, 80]
		    },
		title: {
		text: title,
		    },
		xAxis: {
		categories: data.categories,
		    labels: {
		    rotation: -45,
			align: 'right',
			style: {
			font: 'normal 9px Verdana, sans-serif'
			    }
		}
	    },
		yAxis: {
		min: 0,
		    title: {
		    text: '', //'Population (millions)'
			}
	    },
		legend: {
		enabled: false
		    },
		tooltip: {
		formatter: function() {
		    return '<b>'+ this.x +'</b>: '+ this.y;
		}
	    },
		series: [{
		name: title,
		    data: data.values,
		    dataLabels: {
		    enabled: true,
			rotation: 0,
			color: '#000000', //Highcharts.theme.dataLabelsColor || '#FFFFFF',
			align: 'right',
			x: 0,
			y: 0,
			formatter: function() {
			return this.y;
		    },
			style: {
			font: 'normal 13px Verdana, sans-serif'
			    }
		}         
	    }]
		});
		
}

function helper(container, title, type, model, field) {
    function cb(req) {
	//alert(req);
	var json = eval("("+req+")");
	var data = prepareData(json);
	pieChartFactory(container, title, data);
    }
    var tmp = $.ajax({
	    url: SUB_SITE+"stats/?type="+type+"&model="+model+"&field="+field,
		context: document.body,
		success: cb	    
		});
}

function barHelper(container, title, type, model, field, cutoff) {
    //IF cutoff, then only take the top 20
    function cb(req) {
	//alert(req);
	var json = eval("("+req+")");
	var data = prepareBarData(json);
	if (cutoff) {
	    var size = data.categories.length;
	    data.categories.splice(topCut, size - topCut);
	    data.values.splice(topCut, size - topCut);
	}
	barChartFactory(container, title, data);
    }
    var tmp = $.ajax({
	    url: SUB_SITE+"stats/?type="+type+"&model="+model+"&field="+field,
		context: document.body,
		success: cb	    
		});
}

function init() {
    var graphs = document.getElementById('graphs');
    
    //NOTE: all of the divs are already in dcstats.html
    //top labs by datasets
    barHelper('dataset_lab_div', 'Top Labs by Datasets', 'ssum', 'Datasets', 'paper__lab', true);

    var fields = ['factor', 'platform', 'species', 'cell_type',
	      'cell_line', 'cell_pop', 'strain','condition',
	      'disease_state'];
    for (var i = 0; i < fields.length; i++) {
	var id = fields[i]+"_div";
	helper(id, 'Datasets by '+fields[i], 'sum', 'Datasets', fields[i]);
    }


    //top labs by datasets
    helper('dataset_antibody_div', 'Datasets by Antibody', 'ssum', 'Datasets', 'factor__antibody');

    //tissue types
    helper('dataset_tissue_type_div', 'Datasets by Tissue Type', 'ssum', 'Datasets', 'cell_type__tissue_type');
    
    //papers by journals
    helper('paper_journals_div', 'Papers by Journals', 'sum', 'Papers', 
	   'journal');

    //a little more difficult b/c lab is a virtual field
    helper('paper_lab_div', 'Papers by Labs', 'ssum', 'Papers', 'lab');
    
    //top journals by datasets
    barHelper('dataset_journal_div', 'Top Journals by Datasets', 'ssum', 'Datasets', 'paper__journal', true);
	
}
