document.querySelectorAll(".__range-step").forEach(function (ctrl) {
	var el = ctrl.querySelector('input');
	var output = ctrl.querySelector('output');
	var newPoint, newPlace, offset;
	el.oninput = function () {
		// colorize step options
		ctrl.querySelectorAll("option").forEach(function (opt) {
			if (opt.value <= el.valueAsNumber)
				opt.style.backgroundColor = 'green';
			else
				opt.style.backgroundColor = '#aaa';
		});
		// colorize before and after
		var valPercent = (el.valueAsNumber - parseInt(el.min)) / (parseInt(el.max) - parseInt(el.min));
		var style = 'background-image: -webkit-gradient(linear, 0% 0%, 100% 0%, color-stop(' +
			valPercent + ', green), color-stop(' +
			valPercent + ', #aaa));';
		el.style = style;

		// Popup
		if ((' ' + ctrl.className + ' ').indexOf(' ' + '__range-step-popup' + ' ') > -1) {
			var selectedOpt = ctrl.querySelector('option[value="' + el.value + '"]');
			output.innerText = selectedOpt.text;
			output.style.left = "50%";
			output.style.left = ((selectedOpt.offsetLeft + selectedOpt.offsetWidth / 2) - output.offsetWidth / 2) + 'px';
		}
	};
	el.oninput();
});

window.onresize = function () {
	document.querySelectorAll(".__range").forEach(function (ctrl) {
		var el = ctrl.querySelector('input');
		el.oninput();
	});
};


$(document).ready(function () {
	$("#butt1").click(function () {
		$("#dialog").dialog();
	});
	$("#button2").click(function () {
		$("#page_1").hide();
		$("#page_2").show();
		$("#page_3").hide();
	});
	$("#button3").click(function () {
		$("#page_1").hide();
		$("#page_2").hide();
		$("#page_3").show();
	});
});
