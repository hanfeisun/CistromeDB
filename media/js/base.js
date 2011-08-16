//functions to handle the rollover drop-down menus
//NOTE: we need to add a delayed close b/c otherwise we get usability issues,
//e.g. the user tries to roll onto a link and the menu disappears.
var closetimer= 0;

function open_menu(menu_id) {
    $(menu_id).style.visibility = "visible";
}

function close_menu(menu_id) {
    var timeout = 500; //500ms delay
    closetimer = window.setTimeout(function() {
	    $(menu_id).style.visibility = "hidden";
	}, timeout);
}

function cancel_close(menu_id) {
    if(closetimer) {
	window.clearTimeout(closetimer);
	closetimer = null;
    }
}
