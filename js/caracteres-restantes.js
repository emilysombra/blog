$(document).ready(function(){ 
    $('#charsrestantes').text('500 caracteres restantes');
    $('#msg').keydown(function () {
        var max = 500;
        var len = $(this).val().length;
        if (len >= max) {
            $('#charsrestantes').text('Você atingiu o limite');
            $('#charsrestantes').addClass('red');
            $('#enviar').addClass('disabled');            
        } 
        else {
            var ch = max - len;
            $('#charsrestantes').text(ch + ' caracteres restantes');
            $('#enviar').removeClass('disabled');
            $('#charsrestantes').removeClass('red');            
        }
    });    
});
