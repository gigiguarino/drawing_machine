
function make_ajax(data) {
  $.ajax
  ({
    type: "POST",
    url: "savedata.php",
    data: data,
    cache: false,
    success: function(){
      $.ajax({
        url: "/start",
        type: "POST",
        data: 0,
        error: function (data) {
          console.log('error');
        }
      });
    }
  });
}

function send_array_values() {
  var data = ""
  $('.pixel').each(function(){
    // black = 1
    // red = 2
    // green = 3
    // blue = 4
    var x = this.data('x');
    var y = this.data('y');
    if (this.style.background-color == "black"){
      data += toString(x);
      data += " ";
      data += toString(y);
      data += " ";
      data += "1\n";
    }
    else if (this.style.background-color == "red"){
      data += toString(x);
      data += " ";
      data += toString(y);
      data += " ";
      data += "2\n";
    }
    else if (this.style.background-color == "green"){
      data += toString(x);
      data += " ";
      data += toString(y);
      data += " ";
      data += "3\n";
    }
    else if (this.style.background-color == "blue"){
      data += toString(x);
      data += " ";
      data += toString(y);
      data += " ";
      data += "4\n";
    }
  });
  make_ajax(data);
}

function paint(color) {
  if (color == "white") {
    $(this).css("background-color", "#ffffff");
  }
  else if (color == "black") {
    $(this).css("background-color", "#000000");
  }
  else if (color == "red") {
    $(this).css("background-color", "#ce1010");
  }
  else if (color == "green") {
    $(this).css("background-color", "#008316");
  }
  else if (color == "blue") {
    $(this).css("background-color", "#292ba7");
  }
}

function end_paint() {
  $('.pixel').off(mouseover);
  $('.pixel').off(mouseup);
}

function start_paint(color) {
  $('.pixel').on(mouseover, paint(color));
  $('.pixel').on(mouseup, end_paint());
}

$('#white_marker').click(function(){
  $('.pixel').off(mousedown);
  $('.pixel').on(mousedown, start_paint("white"));
});

$('#black_marker').click(function(){
  $('.pixel').off(mousedown);
  $('.pixel').on(mousedown, start_paint("black"));
});

$('#red_marker').click(function(){
  $('.pixel').off(mousedown);
  $('.pixel').on(mousedown, start_paint("red"));
});

$('#green_marker').click(function(){
  $('.pixel').off(mousedown);
  $('.pixel').on(mousedown, start_paint("green"));
});

$('#blue_marker').click(function(){
  $('.pixel').off(mousedown);
  $('.pixel').on(mousedown, start_paint("blue"));
});



