var cutoff = 0.015;

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

function helper(container, title, model, field) {
    function cb(req) {
	//alert(req);
	var json = eval("("+req+")");
	var data = prepareData(json);
	pieChartFactory(container, title, data);
    }
    var tmp = $.ajax({
	    url: SUB_SITE+"stats/?type=sum&model="+model+"&field="+field,
		context: document.body,
		success: cb	    
		});
}

function init() {
    /*
    function cb(req) {
	//alert(req);
	var json = eval("("+req+")");
	var data = prepareData(json);
	pieChartFactory('disease_state_div', 'Datasets by Disease State', data);
    }
    var tmp = $.ajax({
	    url: SUB_SITE+"stats/?type=sum&model=Datasets&field=disease_state",
		context: document.body,
		success: cb	    
		});
    */
    /*
    helper('disease_state_div', 'Datasets by Disease State', 'Datasets', 
	   'disease_state');
    helper('factor_div', 'Datasets by Factor', 'Datasets', 
	   'factor');
    helper('platform_div', 'Datasets by Platform', 'Datasets', 
	   'platform');
    */
    fields = ['factor', 'platform', 'species', 'cell_type',
	      'cell_line', 'cell_pop', 'strain','condition',
	      'disease_state'];
    var graphs = document.getElementById('graphs');
    for (var i = 0; i < fields.length; i++) {
	var id = fields[i]+"_div";
	var div = $D('div', {'id':id});
	graphs.appendChild(div);
	helper(id, 'Datasets by '+fields[i], 'Datasets', fields[i]);
    }

    //alert($('graphs'));
	
}
