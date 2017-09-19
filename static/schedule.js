$(function(){
	$(".page-form form").submit((e)=>{
		e.preventDefault();
		submitForm(getFormData());
	});
	switch(window.appointmentType) {
		case "life change":
			$("#type").val("2");
			break;
		case "adjustment":
			$("#type").val("1");
			break;
		case "care plan":
			$("#type").val("2");
			break;
		default:
			$("#type").val("1");
	}
});

getFormData = function() {
	return {
		type: $("#type").val(),
		name: $("#name").val(),
		email: $("#email-address").val(),
		phone: $("#phone").val(),
		subscribe: $("#sign-up").prop("checked")
	};
}

submitForm = function(data) {
	$.ajax({
		type: "POST",
		url: "/schedule/signup",
		data: data,
		success: function(res) {
			$(".page-form form").html("<p>Thanks so much for scheduling an appointment! Our team will reach out to you soon!</p>");
		},
		error: function(res) {
			$(".page-form form").html("<p>There was an error submitting a schedule request. We're sorry about that. Give us a call.<a href='tel:+14029334463'>402.933.4463</a>");
		}
	});
}
