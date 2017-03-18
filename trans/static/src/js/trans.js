$(function () {
    $("#tb tbody").append("<tr v-for='line in lines'><td class='t-key'>{{ line.key }}</td><td class='t-us'>{{ line.us }}</td><td class='t-ck'>{{ line.ck }}</td><td class='t-zh'>{{ line.zh }}</td> </tr>");


    var $tb = new Vue({
        el: '#tb',
        data: {
            lines: [
                {key: '1', us: '333', ck: '555', zh: 'fef'},
                {key: '2', us: '333', ck: '555', zh: 'fef'},
                {key: '3', us: '333', ck: '555', zh: 'fef'},
            ]
        }
    });


    $('#upload').on('click', function () {
        $('.page-upload').toggle();
    });


    //初始化fileinput控件（第一次初始化）
    // $('#file-langs').fileinput({
    //     language: 'zh', //设置语言
    //     uploadUrl: "/FileUpload/Upload", //上传的地址
    //     allowedFileExtensions: ['lang', 'py'],//接收的文件后缀,
    //     maxFileCount: 10,
    //     enctype: 'multipart/form-data',
    //     showUpload: true, //是否显示上传按钮
    //     showCaption: false,//是否显示标题
    //     browseClass: "btn btn-primary", //按钮样式
    //     previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
    //     msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",
    // });


    function clear_e() {
        $('#e-us').text("");
        $('#e-ck').text("");
        $('#e-zh').val("");
    }

    $('#tb').on('click', 'tbody tr', function (e) {
        if ($(this).hasClass('seled')) {
            $(this).removeClass('seled');
            clear_e();
        }
        else {
            $('.seled').removeClass('seled');
            $(this).addClass('seled');
            clear_e();
            $('#e-us').text($(this).find('.t-us').text());
            $('#e-ck').text($(this).find('.t-ck').text());
            $('#e-zh').val($(this).find('.t-zh').text());
        }
    });
    $('#e-save').on('click', function () {
        var tmp = $('#e-zh').val();

        $('.seled').data('key', $('.seled').find('.t-key').text())
            .addClass("changed")
            .data('zh', tmp)
            .find('.t-zh').text(tmp);
    });

    function get_changed_data() {
        var changed_data = {};
        _.each($(".changed"), function (cg) {
            changed_data[$(cg).data()['key']] = $(cg).data()['zh']

        });
        return JSON.stringify(changed_data);
    }

    $("#save").on('click', function () {
        $.post("/save", {data: get_changed_data()}, function (datas) {
                console.log(datas);
            }
        )
    });


    //用户选择文件后进行处理
    $('#file-langs').on("change", function (a) {
        $('#upload_file').attr('disabled', 'disabled'); //禁用上传按钮
        var files = $('#file-langs')[0].files;

        if (files.length == 0) {
            alert("文件不能为空！");
            return
        }
        for (var i = 0; i < files.length; i++) {
            if (!s.endsWith(files[i].name, ".lang")) {
                alert("只能上传lang文件");
                return
            }
            if (files[i].size > 1024 * 1024 * 1) {
                alert("逗我呢，有这么大的lang文件？？");
                return
            }
        }


        $('#files').removeData(); // 清空以前绑定的数据

        for (var i = 0; i < files.length; i++) {
            var reader = new FileReader();
            reader.onload = (function (file) {
                return function (e) {
                    $('#files').data(file.name, this.result);
                };
            })(files[i]);
            //读取文件内容
            reader.readAsText(files[i]);
        }

        $('#upload_file').removeAttr('disabled'); //启用上传按钮

    });
    // 上传文件内容
    $('#upload_file')
        .attr('disabled', 'disabled') //禁用上传按钮
        .on('click', function () {
        var data = JSON.stringify($('#files').data());
        $.post("/upload", {data: data}, function (datas) {
                console.log(datas);
            }
        )
    });



});