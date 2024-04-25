(function($){
    var local_path = window.location.pathname, csrfmiddlewaretoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var add_modal_form = "#add_modal_form", edit_modal_form = "#edit_modal_form";
    var variant_boxes = [add_modal_form, edit_modal_form];
    var SETTINGS_DICT = {}, EDIT_DICT={}, SMPPCCM_DICT={};
    var collectionlist_check = function() {
        $.ajax({
            url: local_path + 'manage/',
            type: "POST",
            data: {
                csrfmiddlewaretoken: csrfmiddlewaretoken,
                s:"list",

            },
            dataType: "json",
            success: function(data) {
                var datalist = data;
                var output =  $.map(datalist, function (val, i) {
                    var html = "";
                    var html = `<tr>
                        <td>${i + 1}</td>
                        <td>${val.id}</td>
                        <td>${JSON.stringify(val.cid)}</td>
                        <td>${val.url}</td>
                        <td>${val.email_list}</td>
                        <td class="text-center" style="padding-top:4px;padding-bottom:4px;">
                            <div class="btn-group btn-group-sm">
                                <a href="javascript:void(0)" class="btn btn-light" onclick="return collection_manage('edit', '${val.id}');"><i class="fas fa-edit"></i></a>
                                <a href="javascript:void(0)" class="btn btn-light" onclick="return collection_manage('delete', '${i + 1}');"><i class="fas fa-trash"></i></a>
                            </div>
                        </td>
                    </tr>`;
                    EDIT_DICT[val.id] = val;
                    SETTINGS_DICT[i+1] = val;
                    return html;
                });
                // console.log(output)
            
                $("#collectionlist").html(output);
            
                if (!$.fn.DataTable.isDataTable('#sortable-table')) {
                    $('#sortable-table').DataTable({
                        "pageLength": 25,
                        // other DataTable options...
                    });
                }
            }, error: function(jqXHR, textStatus, errorThrown){quick_display_modal_error(jqXHR.responseText);}
        })
    }
    collectionlist_check();
    window.collection_manage = function(cmd, index){
        index = index || -1;
        if (cmd == "add") {
            showThisBox(variant_boxes, add_modal_form);
            $("#collection_modal").modal("show");
        } else if (cmd == "edit") {
            showThisBox(variant_boxes, edit_modal_form);
    
            var data = EDIT_DICT[index];
            console.log(data)

            $(edit_modal_form + " input[name=id]").val(data.id);
            $(edit_modal_form + " input[name=cid]").val(data.cid);
            $(edit_modal_form + " input[name=url]").val(data.url);
            $(edit_modal_form + " input[name=email_list]").val(data.email_list);
            $("#collection_modal").modal("show");

        } else if (cmd == "smppccm") {
            $.ajax({
                url: main_trans.url2smppccm,
                type: "POST",
                data: {
                    csrfmiddlewaretoken,
                    s: "list",
                },
                dataType: "json",
                success: function (data) {
                    var datalist = data["connectors"];
                    console.log(datalist);
                    var html = $.map(datalist, function (val, i) {
                        SMPPCCM_DICT[i + 1] = val;
                        return `<option>${val.cid}</option>`;
                    });
                    $(add_modal_form + " select[name=cid").html(html);
                    $(edit_modal_form + " select[name=cid]").html(html);
                }
            })
        } else if (cmd == "delete") {
            sweetAlert({
                title: global_trans["areyousuretodelete"],
                text: global_trans["youwontabletorevertthis"],
                type: 'warning',
                showCancelButton: true,
                cancelButtonClass: "btn btn-secondary m-btn m-btn--pill m-btn--icon",
                cancelButtonText: global_trans["no"],
                confirmButtonClass: "btn btn-danger m-btn m-btn--pill m-btn--air m-btn--icon",
                confirmButtonText: global_trans["yes"],
            }, function(isConfirm){
                if (isConfirm) {
                    var data = SETTINGS_DICT[index];
                    $.ajax({
                    	type: "POST",
                    	url: local_path + 'manage/',
                    	data: {
                    		csrfmiddlewaretoken: csrfmiddlewaretoken,
                    		s: cmd,
                    		id: data.id,
                    	},
                    	beforeSend: function(){},
						success: function(data) {
                            toastr.success(data.message, { closeButton: true, progressBar: true });
                            collectionlist_check();
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            toastr.error(jqXHR.responseText, { closeButton: true, progressBar: true });
                        }
                    })
                }
            });
        }
    }
    collection_manage("smppccm");
    $("#add_new_obj").on('click', function(e){collection_manage('add');});
    $(add_modal_form).on("submit", function(e){
        e.preventDefault();
        var serializeform = $(this).serialize();
        // console.log(serializeform);
        var emailTags = [];
        $(".tag span:first-child").each(function () {
            emailTags.push($(this).text().replace(/"/g, "'"));
        });
        
        // Get the email input field value
        var emailInputValue = $("#emailInput").val().trim().replace(/"/g, "");
        
        // Merge email tags and email input value into a single list
        var mergedEmailList = emailTags.concat(emailInputValue.split(/[\s,]+/).filter(email => email !== ''));
        
        // Remove the original email_list parameter from serializeform
        serializeform = serializeform.replace(/&email_list=[^&]*/, '');
        
        // Set the email_list parameter with the merged list as a comma-separated string
        serializeform += "&email_list=" + mergedEmailList.join(',');

        console.log(serializeform);
		var inputs = $(this).find("input, select, button, textarea");
		//inputs.prop("disabled", true);
		$.ajax({
			type: "POST",
			url: $(this).attr("action"),
			data: serializeform,
			beforeSend: function(){inputs.prop("disabled", true);},
			success: function(data){
				toastr.success(data["message"], {closeButton: true, progressBar: true,});
				inputs.prop("disabled", false);
				$(".modal").modal("hide");
				collectionlist_check();
				//setTimeout(location.reload.bind(location), 2000);
			},
			error: function(jqXHR, textStatus, errorThrown){
				toastr.error(JSON.parse(jqXHR.responseText)["message"], {closeButton: true, progressBar: true,});
				inputs.prop("disabled", false);
			}
		});
    });
    $(edit_modal_form).on("submit", function(e){
        e.preventDefault();
        var serializeform = $(this).serialize();
        console.log(serializeform);
		var inputs = $(this).find("input, select, button, textarea");
		$.ajax({
			type: "POST",
			url: $(this).attr("action"),
			data: serializeform,
			beforeSend: function(){inputs.prop("disabled", true);},
			success: function(data){
				toastr.success(data["message"], {closeButton: true, progressBar: true,});
				inputs.prop("disabled", false);
				$(".modal").modal("hide");
				collectionlist_check();
				//setTimeout(location.reload.bind(location), 2000);
			},
			error: function(jqXHR, textStatus, errorThrown){
				toastr.error(JSON.parse(jqXHR.responseText)["message"], {closeButton: true, progressBar: true,});
				inputs.prop("disabled", false);
			}
		});
    });
    setInterval(function () {
        collectionlist_check();
    }, 60000);
    $("li.nav-item.settings-menu").addClass("active");
})(jQuery);