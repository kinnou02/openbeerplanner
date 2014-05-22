// When the DOM is ready, run this function
$(document).ready(function() {
  //Set the carousel options
  $('#quote-carousel').carousel({
    pause: true,
	interval: 0,
  });
});

$("#swipe").swipe({
  swipeLeft:function(event, direction, distance, duration, fingerCount) {
   alert ("tu sux");
  }
});


function hourgetter() {

	value = document.getElementById("rangePrimary").value;
	
	if (value == "1")
	{
		result = "1h00";
	}
	if (value == "2")
	{
		result = "1h30";
	}
	if(value == "3")
	{
		result = "2h00";
	}
	if(value == "4")
	{
		result = "2h30";
	}
	if(value == "5")
	{
		result = "3h00";
	}
	document.getElementById("hour").innerHTML=result;
	document.getElementById("rangePrimaryOutput").value=value;
}

function shoesgetter() {

	value = document.getElementById("rangeSuccess").value;
	
	if (value == "1")
	{
		result = "pantoufle";
	}
	if (value == "2")
	{
		result = "basket";
	}
	if(value == "3")
	{
		result = "rando";
	}
	document.getElementById("shoes").innerHTML=result;
	document.getElementById("rangeSuccessOutput").value=value;
}

function calllist()
{
	value1 = document.getElementById("rangePrimaryOutput").value;
	value2 = document.getElementById("rangeSuccessOutput").value;
}