$(document).ready(function () {

    $('form').on('submit', function (event) {

        $.ajax({
            data: {
                name: $('#name').val(),
            },
            type: 'POST',
            url: '/add_playlist'
        })

            .done(function (data) {
                $('#playlist_res').text(data.message).show();
                $('#playlist_url').text(data.url).attr('href', data.url).show();
                $('#url_div').show()
            });
        event.preventDefault();

    });

});