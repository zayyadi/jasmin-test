(function($){
    var local_path = window.location.pathname, csrfmiddlewaretoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var users_view="#users_view";
    var variant_boxes = [users_view];
    var USERS_DICT = {}; var USER_DICT={};
    function sendEmailNotification(uid) {
        $.ajax({
            url: '/user_stats/send_email_notification/'+ uid,  // Replace with your Django URL
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrfmiddlewaretoken,
                uid: uid,
            },
            dataType: 'json',
            success: function(data) {
                console.log('Success response:', data);
                console.log(data.message);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Error sending email notification:', jqXHR.responseText);
            }
        });
    }
    var collectionlist_check = function(){
        $.ajax({
            url: local_path + 'manage/',
            type: "GET",
            data: {
                s: "list",

            },
            dataType: "json",
            success: function(data){
                var datalist = data["users"];
                var output = $.map(datalist, function(val, i){
                    var statusClass = '';
                
                    // Set class based on status
                     // Red color for DOWN
                    if (val.status === 'BOUND') {
                        statusClass = 'text-success'; // Green color for BOUND
                    } else if (val.status === 'UNBOUND') {
                        statusClass = 'text-danger'; // Yellow color for UNBOUND
                    }
                    var html = "";
                    html += `<tr>
                        <td>${i+1}</td>
                        <td>${val.uid}</td>
                        <td>${val.smpp_bound_conn}</td>
                        <td>${val.smpp_la}</td>
                        <td>${val.http_req_counter}</td>
                        <td>${val.http_la}</td>
                        <td class="text-center" ${statusClass}" style="padding-top:4px;padding-bottom:4px;">${val.status} <i class="fas fa-circle fa-lg ${statusClass}"><i/></td>
                        <td class="text-center" style="padding-top:4px;padding-bottom:4px;">
                            <div class="btn-group btn-group-sm">
                                <a href="javascript:void(0)" class="btn btn-light" onclick="return collection_manage('user', '${val.uid}');"><i class="fas fa-play-circle"></i></a>
                            </div>
                        </td>
                    </tr>`;
                    USERS_DICT[i+1] = val;
                    if (val.smpp_bound_conn == 0) {
                        sendEmailNotification(val.uid);
                    }
                    return html;
                },
                // console.log(data)
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
    window.collection_manage = function(cmd, uid) {
        if (cmd === "user") {
            var datalist;  // Define datalist in the broader scope
    
            $.ajax({
                url: local_path + 'manage/',
                type: "GET",
                data: {
                    s: "user",
                    uid: uid,
                },
                dataType: "json",
                success: function(data) {
                    datalist = data["user"];
                    var output = `
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Items</th>
                                    <th>Type</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Iterate through your data and generate rows -->
                                ${datalist.map((row, index) => `
                                    <tr>
                                        <td>${index + 1}</td>
                                        <td><span style="margin-right: 15px;">${row.item}</span></td>
                                        <td><span style="margin-right: 10px;">${row.types}</span></td>
                                        <td><span style="margin-right: 10px;">${row.value}</span></td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    `;
                    
                    // Populate USER_DICT (if needed)
                    USER_DICT = datalist.reduce((dict, val, i) => {
                        dict[i + 1] = val;
                        return dict;
                    }, {});
    
                    // Append the HTML content to the modal body
                    $("#usersDetailContent").html(datalist.length > 0 ? output : $(".isEmpty").html());
    
                    // Show the modal
                    $("#usersDetailModal").modal("show");
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    quick_display_modal_error(jqXHR.responseText);
                },
            });
        }
    };

            // You can use datalist here if needed, or perform other actions after initiating the AJAX request.
    $("#users_view_obj").on('click', function(e){collection_manage('user');});
    // $(document).ready(function() {
    //     collectionlist_check();
    //   });
    // $("li.nav-item.stats-menu").addClass("active");
    setInterval(function () {
        collectionlist_check();
    }, 10000);
    $("li.nav-item.usersubstats-menu").addClass("active");

})(jQuery);

