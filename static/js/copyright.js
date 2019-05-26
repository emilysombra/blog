$(document).ready(function(){
    var agora = new Date
    var txt = "© " + agora.getFullYear() + " Copyright: Science on the Table"
    document.getElementById('copyright').innerHTML = txt;
});