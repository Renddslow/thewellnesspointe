$(function(){
	$("#sign-up").submit(function(e){
		e.preventDefault();
		submitSimpleForm();
		return false;
	});
});

function submitSimpleForm() {
	var name = $("#firstName").val().trim();
	var email = $("#email").val().trim();
	var type = $("#form-type").val().trim();
	const data = {
		name,
		email,
		type
	}
	$.ajax({
		type: 'POST',
		url: '/signup',
		data,
		success: function(response) {
			$("#sign-up").remove();
			$(".email-message").show().html("Thanks for signing up! You should be hearing from us soon!");
		},
		error: function(response) {
		}
	});
}
