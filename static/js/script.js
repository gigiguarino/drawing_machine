function get_input() {
  var formdata = new FormData($('#upload')[0]);
  $.ajax({
    url: "/upload",
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
