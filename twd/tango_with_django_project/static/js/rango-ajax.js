$(document).ready(function() {

    $('#like_btn').click(function() {
        var catecategoryIdVar;
        catecategoryIdVar = $(this).attr('data-categoryid');

        $.get('/rango/like_category/',
            {'category_id': catecategoryIdVar},
            function(data) {
                $('#like_count').html(data);
                $('#like_btn').hide();
            })
    });

    $('#search-input').keyup(function() {
        var query;
        query = $(this).val();
    
        $.get('/rango/suggest',
            {'suggestion': query},
            function(data) {
                $('#categories-listing').html(data);
            })
    });


    $('.rango-page-add').click(function() {
        var categoryIdVar = $(this).attr('data-categoryid');
        var pageUrlVar = $(this).attr('data-pageurl');
        var pageTitleVar = $(this).attr('data-pagetitle');
        var clickedButton = $(this);
    
        $.get('/rango/search_add_page',
            {'url': pageUrlVar,
             'title': pageTitleVar,
             'category_id': categoryIdVar},

            function(data) {
                $('#pages-listing').html(data);
                clickedButton.hide();
            })
    });
 

});

