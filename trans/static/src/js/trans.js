$(function () {


    $('#upload').on('click', function () {
        $('.page-upload').toggle();
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
                    $('#files').data(file.name.replace('.lang', ""), this.result);
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
                    //console.log(datas);
                    $("#tb tbody")
                        .empty()
                        .append("<tr v-for='line in lines'><td class='t-key'>{{ line.key }}</td><td class='t-ot'>{{ line.ot }}</td><td class='t-ck'>{{ line.ck }}</td><td class='t-zh'>{{ line.zh }}</td> </tr>");
                    //填充数据
                    var lines = JSON.parse(datas);
                    window.ssr = lines;
                    var $tb = new Vue({
                        el: '#tb',
                        data: {
                            lines: lines
                        }
                    });
                    $('#tb tbody')
                        .off()
                        .on('click', 'tr', handle_tr_click);
                }
            )
        });


    var handle_tr_click = function (e) {
        if ($(this).hasClass('seled')) {
            $(this).removeClass('seled');


            $('#e-ot').text("");
            $('#e-ck').text("");
            $('#e-zh').val("");
        }
        else {
            $('.seled').removeClass('seled');
            $(this).addClass('seled');


            // $('#e-ot').text("");
            // $('#e-ck').text("");
            // $('#e-zh').val("");

            $('#e-ot').text($(this).find('.t-ot').text());
            $('#e-ck').text($(this).find('.t-ck').text());
            $('#e-zh').val($(this).find('.t-zh').text());
        }
    }

});