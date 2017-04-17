var color;

$(document).ready(function(){
  color = "white";
  $(".pixel").on("mousedown", start_paint);
  $("#clear").on("click", new_drawing);
  $("#send").on("click", send_array_values);
  $("#white_marker").on("click", function(){
    color = "white";
  });
  $("#black_marker").on("click", function(){
    color = "black";
  });
  $("#red_marker").on("click", function(){
    color = "red";
  });
  $("#green_marker").on("click", function(){
    color = "green";
  });
  $("#blue_marker").on("click", function(){
    color = "blue";
  });
});


function new_drawing(){
  $(".pixel").on("mousedown", start_paint);
  $(".pixel").each(function(){
    $(this).css("background-color", "#ffffff");
  });
}

function make_ajax(data_string){
  $.ajax({
    type: "POST",
    url: "/start",
    data: data_string,
    cache: false,
    success: function(){
      console.log("successfully sent");
    }
  });
}

function send_array_values() {
  $(".pixel").off("mousedown", start_paint);
  var data = ""
  $(".pixel").each(function(){
    // black = 1
    // red = 2
    // green = 3
    // blue = 4
    var x = $(this).data("x");
    var y = $(this).data("y");
    if ($(this).css("background-color") == "rgb(0, 0, 0)"){
      data += x;
      data += " ";
      data += y;
      data += " ";
      data += "1\n";
    }
    else if ($(this).css("background-color") == "rgb(206, 16, 16)"){
      data += x;
      data += " ";
      data += y;
      data += " ";
      data += "2\n";
    }
    else if ($(this).css("background-color") == "rgb(0, 131, 22)"){
      data += x;
      data += " ";
      data += y;
      data += " ";
      data += "3\n";
    }
    else if ($(this).css("background-color") == "rgb(41, 43, 167)"){
      data += x;
      data += " ";
      data += y;
      data += " ";
      data += "4\n";
    }
  });
  make_ajax(data);
}

function paint() {
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
  $(".pixel").off("mouseover", paint);
  $(".pixel").off("mouseup", end_paint);
}

function start_paint() {
  $(".pixel").on("mouseover", paint);
  $(".pixel").on("mouseup", end_paint);
}

