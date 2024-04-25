(function($){
    var local_path = window.location.pathname, csrfmiddlewaretoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var smppc_view="#smppc_view";
    var variant_boxes = [smppc_view];
    var STATS_DICT = {}; var SMPPC_DICT={};
    
    var collectionlist_check = function () {
        $.ajax({
            url: local_path + 'manage/',
            type: "GET",
            data: {
                s: "list",
            },
            dataType: "json",
            success: function (data) {
                var datalist = data["stats"];
                var output = $.map(datalist, function (val, i) {
                    // var statusClass = '';
                
                    // // Set class based on status
                    // if (val.status === 'DOWN') {
                    //     statusClass = 'text-danger'; // Red color for DOWN
                    // } else if (val.status === 'BOUND') {
                    //     statusClass = 'text-success'; // Green color for BOUND
                    // } else if (val.status === 'UNBOUND') {
                    //     statusClass = 'text-warning'; // Yellow color for UNBOUND
                    // }

                    var html = "";
                    html += `<tr>
                        <td>${i + 1}</td>
                        <td>${val.cid}</td>
                        <td>${val.connected_at}</td>
                        <td>${val.bound_at}</td>
                        <td>${val.disconnected_at}</td>
                        <td>${val.submits}</td>
                        <td>${val.delivers}</td>
                        <td>${val.qos_err}</td>
                        <td>${val.other_err}</td>
                        <td class="text-center" style="padding-top:4px;padding-bottom:4px;">
                            <div class="btn-group btn-group-sm">
                                <a href="javascript:void(0)" class="btn btn-light" onclick="return collection_manage('smppc', '${val.cid}');"><i class="fas fa-play-circle"></i></a>
                            </div>
                        </td>
                    </tr>`;
                    STATS_DICT[i + 1] = val;
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

    collectionlist_check();
    // collection_smppc_check();
    window.collection_manage = function(cmd, cid) {
        if (cmd === "smppc") {
            var datalist;  // Define datalist in the broader scope
    
            $.ajax({
                url: local_path + 'manage/',
                type: "GET",
                data: {
                    s: "smppc",
                    cid: cid,
                },
                dataType: "json",
                success: function(data) {
                    datalist = data["smppc"];
                    var output = `
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Items</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Iterate through your data and generate rows -->
                                ${datalist.map((row, index) => `
                                    <tr>
                                        <td>${index + 1}</td>
                                        <td><span style="margin-right: 10px;">${row.item}</span></td>
                                        <td><span style="margin-right: 10px;">${row.value}</span></td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    `;
                    
                    // Populate smppc_DICT (if needed)
                    SMPPC_DICT = datalist.reduce((dict, val, i) => {
                        dict[i + 1] = val;
                        return dict;
                    }, {});
    
                    // Append the HTML content to the modal body
                    $("#smppcDetailContent").html(datalist.length > 0 ? output : $(".isEmpty").html());
    
                    // Show the modal
                    $("#smppcDetailModal").modal("show");
                    
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    quick_display_modal_error(jqXHR.responseText);
                },
            });
        }
    };
    $("#smppc_view_obj").on('click', function(e){collection_manage('smppc');});
    // $(document).ready(function() {
    //     collectionlist_check();
    //   });
    setInterval(function () {
        collectionlist_check();
    }, 10000);
    
    $("li.nav-item.smppsubstats-menu").addClass("active");
})(jQuery);
