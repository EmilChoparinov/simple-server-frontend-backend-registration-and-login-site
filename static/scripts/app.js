console.log('js connected');
$(document).ready(function(){
    $('#tologin').click(function(){
        console.log('b')
        window.location = 'http://localhost:5000/login';
    });
    $('#toregister').click(function(){
        window.location = 'http://localhost:5000/register';
    });
})