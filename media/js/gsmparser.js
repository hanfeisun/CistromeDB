function validPmid(pmid) {
    //returns true if it is an positive integer >= 10000000
    pattern = /^GSM\d+$/;
    return pattern.test(pmid);
}

function validGSEID(gseid) {
    pattern = /^GSE\d{5}$/;
    return pattern.test(gseid);
}

var currPMID = "";
//Function that tries to grab the paper info from ENTREZ dbs
function fetch(pmid) {
    try {
        //var URL = "/entrez/eutils/esummary";
        var URL = SUB_SITE + "ncbiAdapter/GetGSMInfo/";

        var cbFn = function (data) {
            alert(data)
//        try {
//            alert("nima")
//            var tmp = eval("(" + req.responseText + ")");
//            var authorList = tmp.authors;
//            var authors = authorList.join(", ")
//            $('authors').innerHTML = authors;
//
//            var rest = ['title', 'abstract', 'published'];
//            rest.each(function (attr) {
//                $(attr).innerHTML = tmp[attr];
//            });
//
//            $("fetch-form").insert("<p>youmotherisabigfucker</p>")
//            $("fetchBtn").val("Fetch sucessfully!")
//            $("fetchBtn").removeClassName("btn-primary").addClassName("btn-success")
//            $("fetched").show()
//            //currPMID = tmp['pmid'];
//        } catch (err) {
//            console.log(err)
//        }

        }


        var EntrezCall = $.ajax({
            url: URL,
            type: "GET",
            dataType: "json",
            data: {"id": pmid},
            beforeSend: function (xhr) {
                $("#fetchBtn").val("Fetching...")
            },
            success: function (data, status) {
                $.each(data.paper, function(key, value) {
                    if (value instanceof Array) {
                        $("#"+key).html(value.join(", "))}
                    else {
                        $("#"+key).html(value)}
                })


                $.each(data.sample, function(key,value){
                    $("#c_"+key).html(value);
                })
                $("#fetchBtn").val("Fetch sucessfully!")
                $("#fetchBtn").removeClass("btn-primary").addClass("btn-success")
                $("#fetched").show()
                $(".fetch-form").remove()


//                $.each(data.geo, function (i, field) {
//                        var da = $("<label class='col-lg-2 control-label fetch-form'>Series <a href='http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" +
//                            field.gseid + "'>" + field.gseid + "</a></label>" +
//                            '<div class="col-lg-10 fetch-form"><dl id="fetch-form"></dl>' +
//                            '<input type="button" class="btn btn-block btn-primary" value="Import"><hr></div>')
//                        var dl = da.find("#fetch-form")
//                        dl.append("<dt>Title:</dt><dd id='gsetitle' class='value'>" + field.gsetitle + "</dd>")
//                        dl.append("<dt>Species:</dt><dd id='species' class='value'>" + field.species + "</dd>")
//                        dl.append("<dt>Series:</dt><dd id='gseid' class='value'><a href='http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + field.gseid + "'>" + field.gseid + "</a></dd>")
//                        dl.append("<dt>Type:</dt><dd id='type' class='value'>" + field.type + "</dd>")
//                        var gsm_dt = $('<dt>Samples:</dt><dd><table class="table-condensed"><tbody></tbody></table></dd>')
//                        var gsm_ul = gsm_dt.find("tbody")
//                        $.each(field.gsm, function (j, inner_field) {
//                                gsm_ul.append("<tr><td><a href='http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + inner_field.gsmid + "'>"
//                                    + inner_field.gsmid + "</a></td><td>" + inner_field.gsmtitle + "</td></tr>")
//                            }
//                        )
//                        dl.append(gsm_dt)
//                        $("#dataset-big-form").append(da);
//
//
//                    }
//                )


            },
            error: function (xhr, error_info, error_obj) {

                $("#pmid_group").addClass("has-error").find("label").text(error_info + ":" + error_obj)
            }

        });

    } catch (e) {
        console.log(e)
    }
}

function init() {
    $('#fetchBtn').click(function (event) {
        var val = $('#pmid').val();
        if (validPmid(val)) {
            fetch(val);
            currPMID = val;
        } else {
            $("#pmid_group").addClass("has-error").find("label").text("Invalid GSM ID: GSM ID should start with GSM.")
        }
    })

    $("#pmid").keypress(function (event) {
        $("#fetchBtn").val("Fetch metadata");
        $("#fetchBtn").removeClass("btn-success").addClass("btn-primary")
        $("#pmid_group").removeClass("has-error").find("label").text("Pubmed ID:")
    })
    $("#fetched").hide()
//    $('#importBtn').click(function (event) {
//        if (validPMID(currPMID)) {
//            //Just before submission add a hidden input field
//            var pmid = document.createElement('input');
//            pmid.type = "hidden";
//            pmid.name = "pmid";
//            pmid.value = currPMID;
//            $('#autoimport_form').appendChild(gseid);
//        } else {
//            alert("#you must fetch a valid pubmed entry first\n" + val);
//            //break the submission
//            return false;
//        } )
//    }
}
