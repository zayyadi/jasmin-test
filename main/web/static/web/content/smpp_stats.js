(function ($) {
    var local_path = window.location.pathname;
    var smpp_view = "#smpp_view";
    var variant_boxes = [smpp_view];
    var SMPP_DICT = {};

    var collectionlist_check = function () {
        $.ajax({
            url: local_path + 'manage/',
            type: "GET",
            data: {
                s: "list",
            },
            dataType: "json",
            success: function (data) {
                var datalist = data["smppsapi"];
                var output = $.map(datalist, function (val, i) {
                    var html = "";
                    html += `<tr>
                        <td>${i + 1}</td>
                        <td>${val.item}</td>
                        <td>${val.value}</td>
                    </tr>`;
                    SMPP_DICT[i + 1] = val;
                    return html;
                });
                $("#collectionlist").html(datalist.length > 0 ? output : $(".isEmpty").html());
                if (!$.fn.DataTable.isDataTable('#sortable-table')) {
                    $('#sortable-table').DataTable({
                        "pageLength": 25,
                        // other DataTable options...
                    });
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                quick_display_modal_error(jqXHR.responseText);
            }
        });
    };

    // Call the function initially
    collectionlist_check();

    // Set up an interval to call the function every one minute (60,000 milliseconds)
    setInterval(function () {
        collectionlist_check();
    }, 10000);

    // $(document).ready(function() {
    //     collectionlist_check();
    // });

    $("li.nav-item.smppmsubstats-menu").addClass("active");
})(jQuery);
