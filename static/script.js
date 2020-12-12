var names_left = [];
var names_done = [];
var submit_url = "";
var after_submit_url = "";
var time_left = 5;
var countdown_id = null;

function countdown() {
    time_left--;
    if (time_left <= 0) {
	audio = document.getElementById("timesup_audio");
	audio.play();
	setTimeout(turn_over, 1000);
    } 

    if (time_left >= 0) {
	$("#timer").text(time_left.toString() + "s")
    }
}

function start(_submit_url, _after_submit_url) {
    submit_url = _submit_url;
    after_submit_url = _after_submit_url;
    $("#name_to_guess").text(names_left.pop());
    countdown_id = setInterval(countdown, 1000);
}

function next_name(correct) {
    names_done.push([$("#name_to_guess").text(), correct]);
    if (names_left.length > 0) {
	$("#name_to_guess").text(names_left.pop()); 
    } else {
	$("#name_to_guess").text("");
	turn_over();
    }
}

function turn_over() {
    if (!countdown_id) { return; }
    
    clearInterval(countdown_id);
    countdown_id = null;

    console.log(names_done);
    
    if ($("#name_to_guess").text() != "") {
	names_done.push([$("#name_to_guess").text(), false]);
    }
    
    var tr = $("#end_of_turn_area>table>tbody>tr:first");
    var name = names_done.pop();
    $(tr).find("td:first").text(name[0]);
    $(tr).find("#toggle").prop('checked', name[1]);
    
    while (names_done.length > 0) {
	name = names_done.pop();
	tr = tr.after(tr.clone());
	$(tr).find("td:first").text(name[0]);
	$(tr).find("#toggle").prop('checked', name[1]);
    }

    $('#end_of_turn_area').removeClass('hidden');
    $('#play_area').addClass('hidden');
}

function submit_answers() {
    var names_done = [];
    
    $("#end_of_turn_area>table>tbody>tr").each(
	function() {
	    if ($(this).find("#toggle").prop('checked')) {
		names_done.push($(this).find("td:first").text());
	    }});
    
    
    $.ajax(submit_url, {
	data: JSON.stringify(names_done),
	contentType: 'application/json',
	type: 'POST',
	success: function() { location.href = after_submit_url; } });
    
}

