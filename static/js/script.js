function get_input() {
  var formdata = new FormData($('#upload')[0]);
  if ($('#draw_type1').checked && $('#draw_type2').checked)
  {
    alert("please only select one drawing style");
  }
  else if ($('#draw_type1').checked)
  {
    $.ajax({
           url: "/type1",
           type: "POST",
           data: formdata,
           processData: false,
           contentType: false,
           cache: false,
           async: false,
           complete: function (data) {
           console.log('complete');
           },
           error: function (data) {
           console.log('error');
           }
    });
  }
  else if ($('#draw_type2').checked)
  {
    $.ajax({
           url: "/type2",
           type: "POST",
           data: formdata,
           processData: false,
           contentType: false,
           cache: false,
           async: false,
           complete: function (data) {
           console.log('complete');
           },
           error: function (data) {
           console.log('error');
           }
    });
  }
}
