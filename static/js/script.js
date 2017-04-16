


function get_input() {
  var formdata = new FormData($('#upload')[0]);
  if ($('#draw_type1').checked ^ $('#draw_type2').checked ^ $('#draw_type3').checked)
  {
    if ($('#draw_type1').checked)
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
    else if ($('#draw_type3').checked)
    {
      var words = $('#draw_type3_words').toString();
      $.ajax({
             url: "/type3",
             type: "POST",
             data: {data: words},
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
  else if (($('#draw_type1').checked + $('#draw_type2').checked + $('#draw_type3').checked) > 0)
  {
    alert("please only select one.");
  }
}


function get_drawn_values() {
  int[][] array = new int[100][100]
  for (int[] row: array)
  {
    Arrays.fill(row, 0)
  }
  
  
  for (int i = 0; i < 100; i++)
  {
    for (int j = 0; j < 100; j++)
    {
      
    }
  }
}





