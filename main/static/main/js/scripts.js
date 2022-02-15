$(document).ready(() => {

    // let theDiv = JSON.parse(document.getElementById('theDiv').textContent);
    // let theScript = JSON.parse(document.getElementById('theScript').textContent);

    let listColNames = JSON.parse(document.getElementById('listColNames').textContent);
    let dcTable = JSON.parse(document.getElementById('dcTable').textContent);
    let prevDataAvailable; // = JSON.parse(document.getElementById('prevDataAvailable').textContent);
    let keepPrevData = 0;
    let dialog;


    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup(
        {
            type: 'POST',
            url: '/',
            dataType: 'json',
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function (result) {
                let dc_table = result.resp.dc_table;
                prevDataAvailable = result.resp.prev_data_av;
                reDrawTable(dc_table);
                // plotGraph();
                // dialog.modal('hide');
                //sendGvars();

            },
            failure: function (result) {
                console.log(result.responseJSON.errors);
            }
        }
    );

    function reDrawTable(tab) {
        table.fnClearTable();
        table.fnAddData(tab);
        table.fnDraw();
    }

    let lboxSamples = $('#id_lboxSamples').select2({
        placeholder: 'Select a sample(s)',
        multiple: true,
        allowClear: true,
        theme: "classic"
    });

    function setLboxSamples(response) {
        var array = response.samples;
        lboxSamples.select2("val", null);
        lboxSamples.html('').select2({data: []});
        if (array != '') {
            for (idx in array) {
                cur_val = array[idx][0];
                console.log(cur_val);
                let newOption = new Option(cur_val, cur_val, false, false);
                lboxSamples.append(newOption);//.trigger('change');

            }
            lboxSamples.trigger('change'); // Notify any JS components that the value changed
        }
    }


    function setUIElements(response) {
        let resp_gvars = response.resp_gvars;
        for (let prop in resp_gvars) {
            if (prop === 'uncType') {
                let val_r = resp_gvars[prop].toString();
                // $("#id_"+prop+"_"+resp_gvars[prop]).prop('checked', true).trigger('click');
                // $('input[name="uncType"][value=val_r]').attr('checked', true);
                $(`[name="uncType"][value="${val_r}"]`).prop("checked", true);

            } else if (prop === 'rbDiscPerc') {
                let val_r = resp_gvars[prop].toString();
                // $("#id_"+prop+"_"+resp_gvars[prop]).prop('checked', true).trigger('click');
                $(`[name="rbDiscPerc"][value="${val_r}"]`).prop("checked", true);
            } else if (prop === 'chbShowCalc') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbShowCalc"]`).prop("checked", chk);
            } else if (prop === 'chbKeepPrev') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbKeepPrev"]`).prop("checked", chk);
            } else if (prop === 'chbLimitAgeSpectrum') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbLimitAgeSpectrum"]`).prop("checked", chk);
            } else if (prop === 'chbMinAgeCrop') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbMinAgeCrop"]`).prop("checked", chk);
            } else if (prop === 'chbMaxAgeCrop') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbMaxAgeCrop"]`).prop("checked", chk);
            } else if (prop === 'chbIncludeBadEllipses') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbIncludeBadEllipses"]`).prop("checked", chk);
            } else if (prop === 'chbShowErrorBars') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbShowErrorBars"]`).prop("checked", chk);
            } else if (prop === 'chbInclude207235Err') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbInclude207235Err"]`).prop("checked", chk);
            } else if (prop === 'chbShowEllipses') {
                let val_r = resp_gvars[prop].toString();
                let chk = false;
                if (val_r === "on") {
                    chk = true;
                }
                $(`[name="chbShowEllipses"]`).prop("checked", chk);
            } else {
                $("#id_" + prop).val(resp_gvars[prop]);
                $("#id_" + prop).trigger('change');
            }

        }

        var array = response.samples;
        lboxSamples.select2("val", null);
        lboxSamples.html('').select2({data: [null]});
        if (array != '') {
            for (idx in array) {
                cur_val = array[idx][0];
                console.log(cur_val);
                let newOption = new Option(cur_val, cur_val, false, false);
                lboxSamples.append(newOption);//.trigger('change');

            }

            lboxSamples.val(resp_gvars['lboxSamples']);
            lboxSamples.trigger('change'); // Notify any JS components that the value changed
            let selected = lboxSamples.select2('data');
        }

        $("#empModalSession").modal("hide");
    }

    function configureUIElements(frmData) {
        let dataObj = {};

        $(frmData).each(function (i, field) {
            dataObj[field.name] = field.value;
        });

        if (dataObj['cbDensityPlotType'] === "0") {
            $('#id_entKDEBandwidth').removeAttr('readonly');
            $('#id_entHistBinwidth').attr('readonly', true);
        } else if (dataObj['cbDensityPlotType'] === "1") {
            $('#id_entKDEBandwidth').attr('readonly', true);
            $('#id_entHistBinwidth').attr('readonly', true);
        } else if (dataObj['cbDensityPlotType'] === "2") {
            $('#id_entKDEBandwidth').attr('readonly', true);
            $('#id_entHistBinwidth').removeAttr('readonly');
            $('#id_chbShowCalc').prop('checked', false);
        }

        if (dataObj['cbWhichAge'] === "1") {
            $('#id_entAgeCutoff').removeAttr('readonly');
        } else {
            $('#id_entAgeCutoff').attr('readonly', true);
        }

        if (dataObj['cbPbc'] === "4" || dataObj['cbPbc'] === "3" || dataObj['cbPbc'] === "2") {
            $('#id_cbWhichAge').prop('disabled', true);
            $('#id_entAgeCutoff').attr('readonly', true);
            $('#id_cbWhichConc').prop('disabled', true);
            $('#id_entDiscAgeFixedLim').attr('readonly', true);
            $('#id_entNegDiscFilt').attr('readonly', true);
            $('#id_entPosDiscFilt').attr('readonly', true);
        }
        if (dataObj['cbPbc'] === "0" || dataObj['cbPbc'] === "1") {
            $('#id_cbWhichAge').prop('disabled', false);
            $('#id_entAgeCutoff').removeAttr('readonly');
            $('#id_cbWhichConc').prop('disabled', false);
            $('#id_entDiscAgeFixedLim').removeAttr('readonly');
            $('#id_entNegDiscFilt').removeAttr('readonly');
            $('#id_entPosDiscFilt').removeAttr('readonly');
        }
        if (dataObj['cbPbc'] === "4") {
            $('#id_entAgeAndersen').removeAttr('readonly');
        } else {
            $('#id_entAgeAndersen').attr('readonly', true);
        }
        if (dataObj['cbWhichAge'] === "1") {
            $('#id_entAgeCutoff').removeAttr('readonly');
        } else {
            $('#id_entAgeCutoff').attr('readonly', true);
        }

        if (dataObj['cbWhichConc'] === "0") {
            $('#id_entDiscAgeFixedLim').removeAttr('readonly');
        } else {
            $('#id_entDiscAgeFixedLim').attr('readonly', true);
        }

        if (dataObj['rbDiscPerc'] === "0") {
            $('#id_cbDiscIntersect').prop('disabled', true);
        } else {
            $('#id_cbDiscIntersect').prop('disabled', false);
        }

        if (dataObj['cbErrFilter'] === "1") {
            $('#id_entErrFilter').removeAttr('readonly');
            $('#id_chbInclude207235Err').prop("disabled", false);//.removeAttr('readonly');

        } else if (dataObj['cbErrFilter'] === "0") {
            $('#id_entErrFilter').attr('readonly', true);
            $('#id_chbInclude207235Err').prop("disabled", true);//.attr('readonly', true);
        }

        if (dataObj['cbUConc'] === "1") {
            $('#id_entUconcCutoff').removeAttr('readonly');
        } else {
            $('#id_entUconcCutoff').attr('readonly', true);
        }

        if (dataObj['chbMinAgeCrop'] === "on") {
            $('#id_entAgeMinCrop').removeAttr('readonly');
        } else {
            $('#id_entAgeMinCrop').attr('readonly', true);
        }

        if (dataObj['chbMaxAgeCrop'] === "on") {
            $('#id_entAgeMaxCrop').removeAttr('readonly');
        } else {
            $('#id_entAgeMaxCrop').attr('readonly', true);
        }

        if (dataObj['chbKeepPrev'] === "on") {
            $('#id_chbLimitAgeSpectrum').prop('checked', false);
            // $('#id_chbLimitAgeSpectrum').attr('readonly', true);
        } else {
            // $('#id_chbKeepPrev').prop('checked', true);
            // $('#id_chbLimitAgeSpectrum').removeAttr('readonly');
        }

        if (dataObj['chbLimitAgeSpectrum'] === "on") {
            $('#id_chbKeepPrev').prop('checked', false);
            // $('#id_chbKeepPrev').attr('readonly', true);
        } else {
            // $('#id_chbKeepPrev').prop('checked', true);
            // $('#id_chbKeepPrev').removeAttr('readonly');
        }

        if ( typeof dataObj['chbShowEllipses'] === "undefined") {

            // $('#id_chbIncludeBadEllipses').prop('checked', false);
            // $('#id_chbIncludeBadEllipses').attr('readonly', true);
            // $('#id_chbIncludeBadEllipses').prop("disabled", true);

            $('#id_chbShowErrorBars').prop('checked', true);
            $('#id_chbShowErrorBars').attr('readonly', true);
            $('#id_chbShowErrorBars').prop("disabled", true);


        } else {

            if (dataObj['chbShowEllipses'] === "on") {
                console.log()

            $('#id_chbShowErrorBars').removeAttr('readonly');
            $('#id_chbIncludeBadEllipses').attr('readonly', false);
            $('#id_chbIncludeBadEllipses').removeAttr('readonly');
            $('#id_chbIncludeBadEllipses').prop("disabled", false);

            $('#id_chbShowErrorBars').removeAttr('readonly');
            $('#id_chbShowErrorBars').prop("disabled", false);

            }

        }

    }

    $.fn.dataTable.Buttons.defaults.dom.button.className = 'btn btn-primary';
    $.fn.dataTable.Buttons.defaults.dom.button.className = 'btn';

    $.fn.dataTable.ext.buttons.loaddata = {
        text: 'Import file',
        attr: {
            title: 'Import file',
            id: 'importButton',
            className: 'btn btn-danger'
        },
        action: function (e, dt, node, config) {
            // window.location.href = '../uploads/form/';
            beginUploadFile();
        }
    };

    $.fn.dataTable.ext.buttons.plot = {
        text: 'Plot graph',
        attr: {
            title: 'Plot graph',
            id: 'plotButton',
            className: 'btn btn-success pl-3'
        },
        action: function (e, dt, node, config) {
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'ajax_save',
                    'number_in_list': -1,
                    'form_field': 'ajax_save'
                },
                success: function (result) {

                    plotGraph();
                }
            });
        }
    };

    let table = $('#tabSamples').dataTable({
        dom: "Bfrtip",
        "createdRow": function (row, data, dataIndex) {
            if (data["isgraingood?"] == "False") {
                $(row).addClass('red');
            }
        },
        searching: false,
        retrieve: true,
        destroy: true,
        pageLength: 5,
        lengthMenu: [5, 10, 20, 30, 50, 100],
        "pagingType": "full_numbers",
        "data": dcTable,
        "columns": listColNames,
        "columnDefs": [{
            "targets": '_all',
            "defaultContent": ""
        }],
        fixedColumns: {
            left: 1
        },
        buttons: {
            buttons: [
                {text: 'Step 1:', className: 'font-weight-bold'},
                {extend: 'loaddata', className: 'btn btn-secondary'},
                {text: 'Step 2: Choose filters and algorithms below', className: 'font-weight-bold'},
                {text: 'Step 3:', className: 'font-weight-bold'},
                {
                    text: 'PLOT!',
                    className: 'btn btn-success',
                    titleAttr: 'Plot graph',
                    // init: function (dt, node, config) {
                    // },
                    action: function (e, dt, node, config) {
                        // window.location.href = '../uploads/form/';
                        var formData = $('#id_frm').serializeArray();
                        formData = JSON.stringify(formData);
                        $.ajax({
                            data: {
                                "form_data": formData,
                                'type_event': 'ajax_save',
                                'number_in_list': -1,
                                'form_field': 'ajax_save'
                            },
                            type: 'POST',
                            url: '/',
                            dataType: 'json',
                            beforeSend: function (xhr, settings) {
                                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                                }
                            },
                            success: function (result) {
                                let dc_table = result.resp.dc_table;
                                prevDataAvailable = result.resp.prev_data_av
                                table.fnClearTable();
                                table.fnAddData(dc_table);
                                table.fnDraw();
                                plotGraph();
                                // sendGvars();
                            }
                        });


                    }
                },
                {text: 'Step 4:', className: 'font-weight-bold'},
                {
                    text: 'Show stats',
                    className: 'btn btn-secondary',
                    titleAttr: 'Statistics',
                    action: function (e, dt, node, config) {
                        $.ajax({
                            url: '/statistics/',
                            dataType: 'json',
                            // data: {"g_grainset": ggrainset},
                            header: {'X-CSRFToken': csrftoken},
                            success: function (result) {
                                bootbox.alert({
                                    message: result,
                                    //size: 'large'
                                });

                            }
                        });
                        return false;
                    }
                },
                {text: 'Step 5:', className: 'font-weight-bold'},
                {extend: 'csv', text: 'Export data', className: 'btn btn-secondary'},
            ],
            dom: {
                button: {
                    className: 'btn mb-2'
                }
            }
        },
        drawCallback: function () {
            // Pagination - Add BS4-Class for Horizontal Alignment (in second of 2 columns) & Top Margin
            // $('#tabSamples_wrapper .col-md-7:eq(0)').addClass("d-flex justify-content-center justify-content-md-end");
            $('#tabSamples_paginate').addClass("mt-3 mt-md-2");
            $('#tabSamples_paginate ul.pagination').addClass("pagination-sm");


        }

    });

    $('#tabSamples_wrapper .col-md-7:eq(0)').addClass("d-flex justify-content-center justify-content-md-end");
    $('#tabSamples_paginate').addClass("mt-3 mt-md-2");
    $('#tabSamples_paginate ul.pagination').addClass("pagination-sm");


// ===========================================================================================

    $("#id_uncType").change(function (event) {
            // alert('uncType')
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 23,
                    'form_field': 'uncType'
                },
                success: function (result) {
                    let dc_table = result.resp.dc_table;
                    reDrawTable(dc_table);
                    // plotGraph();

                }
            });
        }
    );

    lboxSamples.change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': -1,
                    'form_field': 'lboxSamples'
                },
                success: function (result) {
                    let dc_table = result.resp.dc_table;
                    reDrawTable(dc_table);
                    // plotGraph();

                }
            });
        }
    );

    $('#id_cbWhichAge').select2({
        theme: "bootstrap4"
    });
    $("#id_cbWhichAge").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);
            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 3,
                    'form_field': 'cbWhichAge'
                }
            });
        }
    );
    $("#id_entAgeCutoff").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 19,
                    'form_field': 'entAgeCutoff'
                }
            });
        }
    );

    $('#id_cbPbc').select2({
        theme: "bootstrap4"
    });
    $("#id_cbPbc").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);

            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 4,
                    'form_field': 'cbPbc'
                }
            });
        }
    );

    var entAgeAndersen = $('#id_entAgeAndersen')
    var timeOut;

    entAgeAndersen.on('keyup', function (event) {
        clearTimeout(timeOut);
        timeOut = setTimeout(funcOnChange, 2000, $(this).val());

    });
    entAgeAndersen.on('keydown', function (event) {
        clearTimeout(timeOut);
    });

    function funcOnChange(value) {
        var formData = $('#id_frm').serializeArray();
        formData = JSON.stringify(formData);
        $.ajax({
            data: {
                "form_data": formData,
                'type_event': 'onChange',
                'number_in_list': 28,
                'form_field': 'entAgeAndersen'
            }
        });
        //alert(value)
    }


    // $("#id_entAgeAndersen").change(function (event) {
    //         event.preventDefault();
    //         var formData = $('#id_frm').serializeArray();
    //         formData = JSON.stringify(formData);
    //         $.ajax({
    //             data: {
    //                 "form_data": formData,
    //                 'type_event': 'onChange',
    //                 'number_in_list': 28,
    //                 'form_field': 'entAgeAndersen'
    //             }
    //         });
    //     }
    // );

    $('#id_cbWhichConc').select2({
        theme: "bootstrap4"
    });
    $("#id_cbWhichConc").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);

            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 8,
                    'form_field': 'cbWhichConc'
                }
            });
        }
    );
    $("#id_entDiscAgeFixedLim").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 25,
                    'form_field': 'entDiscAgeFixedLim'
                }
            });
        }
    );
    $("#id_rbDiscPerc").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();

            formData = JSON.stringify(frmData);
            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 29,
                    'form_field': 'rbDiscPerc'
                }
            });
        }
    );
    //     $("#id_rbDiscPerc").change(
    //     function () {
    //         var val = $(this).val(); // retrieve the value
    //             console.log(val);
    //         // var curVal = $("#id_rbDiscPerc").val();
    //         // // var cur_values = getCurValues();
    //         // // console.log(cur_values);
    //         // console.log(curVal);
    //         //
    //         // if (curVal === '1') {
    //         //     $('#id_cbDiscIntersect').attr('readonly', true);
    //         // } else {
    //         //     $('#id_cbDiscIntersect').attr('readonly', true);
    //         // }
    //     }
    // );


    $("#id_entNegDiscFilt").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 7,
                    'form_field': 'entNegDiscFilt'
                }
            });
        }
    );
    $("#id_entPosDiscFilt").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 6,
                    'form_field': 'entPosDiscFilt'
                }
            });
        }
    );

    $('#id_cbDiscIntersect').select2({
        theme: "bootstrap4"
    });
    $("#id_cbDiscIntersect").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 30,
                    'form_field': 'cbDiscIntersect'
                }
            });
        }
    );

    $('#id_cbErrFilter').select2({
        theme: "bootstrap4"
    });
    $("#id_cbErrFilter").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);

            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 5,
                    'form_field': 'cbErrFilter'
                }
            });
        }
    );
    $("#id_entErrFilter").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 20,
                    'form_field': 'entErrFilter'
                }
            });
        }
    );

    $('#id_cbUConc').select2({
        theme: "bootstrap4"
    });
    $("#id_cbUConc").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);

            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 2,
                    'form_field': 'cbUConc'
                }
            });
        }
    );
    $("#id_entUconcCutoff").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 18,
                    'form_field': 'entUconcCutoff'
                }
            });
        }
    );
    $("#id_chbInclude207235Err").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 22,
                    'form_field': 'chbInclude207235Err'
                }
            });
        }
    );

    $('#id_cbConcType').select2({
        theme: "bootstrap4"
    });
    $("#id_cbConcType").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 0,
                    'form_field': 'cbConcType'
                }
            });
        }
    );

    $('#id_cbEllipsesAt').select2({
        theme: "bootstrap4"
    });
    $("#id_cbEllipsesAt").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 2,
                    'form_field': 'cbEllipsesAt'
                }
            });
        }
    );

    $('#id_cbShowUncorrCorrBothEllipses').select2({
        theme: "bootstrap4"
    });
    $("#id_cbShowUncorrCorrBothEllipses").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': -1,
                    'form_field': 'cbShowUncorrCorrBothEllipses'
                }
            });
        }
    );

    $('#id_cbDensityPlotType').select2({
        theme: "bootstrap4"
    });
    $("#id_cbDensityPlotType").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);
            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 7,
                    'form_field': 'cbDensityPlotType'
                }
            });
        }
    );

    $("#id_entKDEBandwidth").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 11,
                    'form_field': 'entKDEBandwidth'
                }
            });
        }
    );
    $("#id_entHistBinwidth").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 12,
                    'form_field': 'entHistBinwidth'
                }
            });
        }
    );
    $("#id_chbMinAgeCrop").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);

            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 26,
                    'form_field': 'chbMinAgeCrop'
                }
            });
        }
    );
    $("#id_entAgeMinCrop").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 261,
                    'form_field': 'entAgeMinCrop'
                }
            });
        }
    );
    $("#id_chbMaxAgeCrop").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);

            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 27,
                    'form_field': 'chbMaxAgeCrop'
                }
            });
        }
    );
    $("#id_entAgeMaxCrop").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onChange',
                    'number_in_list': 271,
                    'form_field': 'entAgeMaxCrop'
                }
            });
        }
    );
    $("#id_chbShowCalc").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            // console.log('FORM_DATA = ' + formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 33,
                    'form_field': 'chbShowCalc'
                },
                success: function (result) {
                    let dc_table = result.resp.dc_table;
                    reDrawTable(dc_table);
                    plotGraph();

                }
            });
        }
    );
    // $("#id_chbShowCalc").change(function (event) {
    //         event.preventDefault();
    //         var formData = $('#id_frm').serializeArray();
    //         formData = JSON.stringify(formData);
    //         console.log('FORM_DATA = ' + formData);
    //         $.ajax({
    //             data: {
    //                 "form_data": formData,
    //                 'type_event': 'onGraphChange',
    //                 'number_in_list': 33,
    //                 'form_field': 'chbShowCalc'
    //             }
    //         });
    //     }
    // );
    $("#id_chbKeepPrev").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);

            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 13,
                    'form_field': 'chbKeepPrev'
                },
                success: function (result) {
                    let dc_table = result.resp.dc_table;
                    reDrawTable(dc_table);
                    plotGraph();

                }
            });
        }
    );
    $("#id_chbLimitAgeSpectrum").change(function (event) {
            event.preventDefault();
            var frmData = $('#id_frm').serializeArray();
            formData = JSON.stringify(frmData);

            configureUIElements(frmData);

            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 131,
                    'form_field': 'chbLimitAgeSpectrum'
                },
                success: function (result) {
                    let dc_table = result.resp.dc_table;
                    reDrawTable(dc_table);
                    plotGraph();

                }
            });
        }
    );
    $("#id_chbIncludeBadEllipses").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 32,
                    'form_field': 'chbIncludeBadEllipses'
                },
                success: function (result) {
                    let dc_table = result.resp.dc_table;
                    reDrawTable(dc_table);
                    // plotGraph();

                }
            });
        }
    );
    $("#id_chbShowErrorBars").change(function (event) {
            event.preventDefault();
            var formData = $('#id_frm').serializeArray();
            formData = JSON.stringify(formData);
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 34,
                    'form_field': 'chbShowErrorBars'
                },
                success: function (result) {
                    let dc_table = result.resp.dc_table;
                    reDrawTable(dc_table);
                    // plotGraph();

                }
            });
        }
    );

    $("#id_chbShowEllipses").change(function (event) {
            event.preventDefault();
            let frmData = $('#id_frm').serializeArray();
            let formData = JSON.stringify(frmData);
            configureUIElements(frmData)
            $.ajax({
                data: {
                    "form_data": formData,
                    'type_event': 'onGraphChange',
                    'number_in_list': 35,
                    'form_field': 'chbShowEllipses'
                },
                success: function (result) {
                    let dc_table = result.resp.dc_table;
                    reDrawTable(dc_table);
                    // plotGraph();

                }
            });
        }
    );

    // ==============================================================================


    $('#ajax_save').click(function (event) {
        event.preventDefault();
        var formData = $('#id_frm').serializeArray();
        formData = JSON.stringify(formData);
        $.ajax({
            data: {
                "form_data": formData,
                'type_event': 'ajax_save',
                'number_in_list': -1,
                'form_field': 'ajax_save'
            },
            success: function (result) {
                plotGraph();
            }
        });

    });

    function sendGvars() {
        //event.preventDefault();
        $.ajax({
            url: '/bokeh/',
            data: {'gvars': gvars},
            dataType: 'json',
            header: {'X-CSRFToken': csrftoken},
            success: function (result) {
                // console.log(result)
                plotGraph();
            }
        });
        return false;
    }


    function plotGraph() {
        //event.preventDefault();
        dialog = bootbox.dialog({
            message: '<p class="text-center mb-0"><i class="fas fa-spin fa-cog"></i> Please wait while the graph is plotting ...</p>',
            closeButton: false
        });

        $.ajax({
            url: '/bokeh/',
            dataType: 'json',
            header: {'X-CSRFToken': csrftoken},
            success: function (result) {
                console.log("BOKEH" + result.success)
                // console.log(result)
                if (result.success === false) {
                    bootbox.alert({
                        centerVertical: true,
                        message: "No good grains!",
                        size: 'small'
                    });
                }
                $('#bokeh_graph_ax_conc').html(result.div_ax_conc + result.script_ax_conc);
                // $('#bokeh_graph_ax_conc').html(result.div_ax_conc);
                $('#bokeh_graph_ax_prob').html(result.div_ax_prob + result.script_ax_prob);
                $('#bokeh_graph_ax_cum').html(result.div_ax_cum + result.script_ax_cum);
                // $("head").append(result.script);
                setTimeout(function () {
                    dialog.modal('hide');
                }, 500);
            }
        });
        return false;
    }


    $('#ajax_bokeh').click(function (event) {
        event.preventDefault();
        var formData = $('#id_frm').serializeArray();
        formData = JSON.stringify(formData);
        $.ajax({
            data: {
                "form_data": formData,
                'type_event': 'ajax_save',
                'number_in_list': -1,
                'form_field': 'ajax_save'
            },
            beforeSend: function () {

            },
            success: function (result) {

                plotGraph();
            }
        });
    });

    $('#ajax_stat').click(function (event) {
        event.preventDefault();
        $.ajax({
            url: '/statistics/',
            dataType: 'json',
            header: {'X-CSRFToken': csrftoken},
            success: function (result) {
                // Add response in Modal body
                $('.modal-body').html(JSON.stringify(result));

                // Display Modal
                $('#empModal').modal('show');
            }
        });
        return false;
    });

    function showUploadFileDialog() {
        $.ajax({
            url: '/uploads/form/',
            type: 'get',
            dataType: 'json',
            header: {'X-CSRFToken': csrftoken},
            beforeSend: function () {

                $("#empModal .modal-title").html("Upload file");
                $("#empModal").modal("show");
            },
            success: function (result) {
                console.log(result)
                $("#empModal .modal-body").html(result.html_form);
            }
        });

    }

    function beginUploadFile() {
        if (prevDataAvailable) {
            bootbox.confirm({
                message: "Keep previous data?",
                centerVertical: true,
                buttons: {
                    confirm: {
                        label: 'Yes',
                        className: 'btn-success'
                    },
                    cancel: {
                        label: 'No',
                        className: 'btn-danger'
                    }
                },
                callback: function (result) {
                    console.log(result)
                    if (result === true) {
                        keepPrevData = 1;
                    } else {
                        keepPrevData = 0;
                    }
                    $.post("/getkeepprevdata/", {"keep_prev_data": keepPrevData}, function (result) {
                        console.log(result);
                        showUploadFileDialog();
                    });

                }
            });
        } else {
            // keepPrevData = 0;
            showUploadFileDialog();
        }
    }

    $('#ajax_load_file').click(function (event) {
        event.preventDefault();
        beginUploadFile();
    });


    $('#empModal').on('submit', function (e) {
        e.preventDefault();

        var data = new FormData($('#fileUpload').get(0));
        // $.post("/getkeepprevdata/", {"keep_prev_data": keepPrevData});
        $.ajax({
            url: "/uploads/form/",
            method: "POST",
            data: data,
            dataType: 'json',
            header: {'X-CSRFToken': csrftoken},
            processData: false,
            contentType: false,
            beforeSend: function () {
                //$.post("/getkeepprevdata/", {"keep_prev_data": keepPrevData});
                $('#msg').html('<div class="alert alert-warning"><strong>Please wait! Loading ...</strong></div>');
            },
            success: function (response) {
                prevDataAvailable = response.prev_data_av;
                setLboxSamples(response);
                console.log(keepPrevData)
                $('#msg').html(response.msg);
                // $('#status').html('<div id="status" class="alert " ' + response.status_alert + ' " p-1 m-1"><strong>Status: </strong>' + response.status_text + '</div>');
                $('#status').html(response.status_text);
                $('#uploaded_file').html(response.filename);
                let dc_table = response.dc_table;
                reDrawTable(dc_table);

                let frmData = $('#id_frm').serializeArray();
                configureUIElements(frmData);

                $("#empModal").modal("hide");
            },
            error: function (response) {
                alert('ERROR');
                $('#msg').html(response.message);
                // $("#empModal").modal("hide");
            }
        });
        return false;
    });

    $('#ajax_load_session').click(function (event) {
        event.preventDefault();
        $.ajax({
            url: '/uploads/sessions/',
            type: 'get',
            dataType: 'json',
            header: {'X-CSRFToken': csrftoken},
            beforeSend: function () {
                $("#empModalSession .modal-title").html("Upload session");
                $("#empModalSession").modal("show");
            },
            success: function (result) {
                console.log(result)
                $("#empModalSession .modal-body").html(result.html_form);
            }
        });
    });

    $('#empModalSession').on('submit', function (e) {
        e.preventDefault();

        var data = new FormData($('#sessionUpload').get(0));
        $.ajax({
            url: "/uploads/sessions/",
            method: "POST",
            data: data,
            dataType: 'json',
            header: {'X-CSRFToken': csrftoken},
            processData: false,
            contentType: false,
            beforeSend: function () {
                $('#msg').html('<div class="alert alert-warning"><strong>Please wait! Loading ...</strong></div>');
            },
            success: function (response) {
                setUIElements(response)
                let dc_table = response.dc_table;
                reDrawTable(dc_table);

                let frmData = $('#id_frm').serializeArray();
                configureUIElements(frmData);

                $('#msgSession').html(response.msg);
                // $("#empModalSession").modal("hide");
            },
            error: function (response) {
                alert('ERROR');
                $('#msgSession').html(response.message);
                //$("#empModalSession").modal("hide");
            }
        });
        return false;
    });


});

