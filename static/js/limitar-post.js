$(document).ready(function(){
  var max_len = 250;
  var i;
  for(i = 1; i <= 10; i++){
    var index = String(i);
    if(document.getElementById(index) != null){
      txt = document.getElementById(index).innerHTML;
      if(txt.length > max_len){
        var txt = txt.substr(0, max_len) + '...';

      }
      uau = index + '-' + String(txt.length)
      console.log(uau);
      document.getElementById(index).innerHTML = txt;
    }
  }
});