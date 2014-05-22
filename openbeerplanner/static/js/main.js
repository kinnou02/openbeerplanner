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
