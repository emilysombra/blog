$(document).ready(function(){
    var agora = new Date
    var txt = "© " + agora.getFullYear() + " Copyright: The Science's on the Table"
    document.getElementById('copyright').innerHTML = txt;
});