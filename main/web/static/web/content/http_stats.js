(function($){
    var local_path = window.location.pathname;
    var http_view="#http_view";
    var variant_boxes = [http_view];
    var HTTP_DICT = {};
    var collectionlist_check = function(){
        $.ajax({
            url: local_path + 'manage/',
            type: "GET",
            data: {
                s: "list",

            },
            dataType: "json",
            success: function(data){
                var datalist = data["httpapi"];
                var output = $.map(datalist, function(val, i){
                    var html = "";
                    html += `<tr>
                        <td>${i+1}</td>
                        <td>${val.item}</td>
                        <td>${val.value}</td>
                    </tr>`;
                    HTTP_DICT[i+1] = val;
                    return html;
                },
                console.log(data)
                );
                $("#collectionlist").html(datalist.length > 0 ? output : $(".isEmpty").html());
                if (!$.fn.DataTable.isDataTable('#sortable-table')) {
                    $('#sortable-table').DataTable({
                        "pageLength": 25,
                        // other DataTable options...
                    });
                }
            }, error: function(jqXHR, textStatus, errorThrown){quick_display_modal_error(jqXHR.responseText);}
        });
    };
    collectionlist_check();
    setInterval(function () {
        collectionlist_check();
    }, 600);
    $("li.nav-item.httpmsubstats-menu").addClass("active");
})(jQuery);