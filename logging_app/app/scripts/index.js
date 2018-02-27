function findBaseName(url) {
    var fileName = url.substring(url.lastIndexOf('/') + 1);
    var dot = fileName.lastIndexOf('.');
    return dot == -1 ? fileName : fileName.substring(0, dot);
}

$(function() {
    $(".tabcontent").hide() 
    
    $(".tablinks").click(function(e) {
            e.preventDefault();
            var id=$(this).attr("data-id")
            var query = ''
            var i, tabcontent, tablinks;
            $(".tabcontent").hide()
            $(".tablinks").removeClass("active")
            $("#Question"+id).show()
            $(this).addClass("active")
            if(id=="search")
                query = $("#searchtext").val()
            else
                query = $("#Question"+id).find("p").text()
            query = encodeURIComponent(query)
            console.log("http://localhost:8983/solr/mycore/select?q=content:"+query)
            var data={}
            data.query=query
            var t = ''
            if(id == "search")
                t = '<h4><b>Suggestions</b></h4>'
            t += "<table class='table table-striped'>" 
            t+= "<tr><td><b>S.No</b></td><td><b>URL</b></td><td><b>Title</b></td><td><b>Score</b></td><td><b>Content</b></td></tr>"
            //t += "<colgroup><col width='10%'><col width='10%'><col width='10%'> <col width='70%'> </colgroup>"
            $.get("http://localhost:8000/solr",data)
            .done(function(msg){
                var  j = 1
                $.each(JSON.parse(msg), function(i, v) {
                     console.log(findBaseName(v.url.toString()))
                     t += "<tr><td>"+j+"  </td><td ><a class='url' href='"+v.url+"'> '"+v.url+"' </a></td><td>"+v.title+"</td><td>"+v.score+"</td><td >"+v.content.replace(/\n+/g, "<br />")+"</td></tr>"
                     j = j + 1
                 });
                t+="</table>"
                if(id == "search")
                    $("#searchsuggestions").html(t)
                else
                    $("#suggestion"+id).html(t);    

            }).fail(function(response) {
                console.log("fail")
            });;
        });  
});