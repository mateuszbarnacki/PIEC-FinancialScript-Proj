window.addEventListener('load', () => {
	const lastWeekCheck = document.getElementById('lastWeekCheck');
	const lastMonthCheck = document.getElementById('lastMonthCheck');

	lastWeekCheck.addEventListener("change", e => {
		if(lastWeekCheck.checked){
			document.getElementById('lastWeekDiv').innerHTML = "<img src='../img/lastFiveMean.png' />";
		} else {
			document.getElementById('lastWeekDiv').innerHTML = "<img src='../img/lastFive.png' />";
		}
	});

	lastMonthCheck.addEventListener("change", e => {
		if(lastMonthCheck.checked){
			document.getElementById('lastMonthsDiv').innerHTML = "<img src='../img/lastMonthsMean.png' />";
		} else {
			document.getElementById('lastMonthsDiv').innerHTML = "<img src='../img/lastMonths.png' />";
		}
	});
});
