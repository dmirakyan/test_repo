$(document).ready(function(){
    // alert('Hello, world!');
})

$(document).ready(function() {

    $('#about-btn').click(function() {
        alert('You clicked this using a better approach to Jquery!');
    });


    $('#about-btn').click(function() {
        msgStr = $('#msg').html();
        msgStr = msgStr + 'oo, fancy!';
    
        $('#msg').html(msgStr);
    });

    $('.ouch').click(function() {
        alert('You clicked me! Ouch!');
    });
    
    
    $('p').hover(
        function() {
            $('p').css('color', 'red');
        }, 
        function() {
            $('p').css('color', 'black');
    });    

    $( "#about-btn" ).click(function() {
        $( "#catpic" ).slideDown( "slow", function() {
          // Animation complete.
        });
      });

});


