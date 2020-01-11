$(function () {
    var btn = $('form input[name=submit]');
    var pwd = $('form input[name=passport]');
    btn.hide();

})
pwd.change(function () {
    var re = /\w{6,20}/;
    btn.show();
    // console.log(pwd.text());
    if (re.exec(pwd.text())) {
        btn.show();
    }
})