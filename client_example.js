var makePicTable = function(dataObj){

  var picImg = "<a href='/mobile_pix/"+dataObj['big']+"' title='"+dataObj['story']+"'>";
  picImg += "<img src='/mobile_pix/"+dataObj['small']+"'/></a>";
  var picRow = "<tr><td cellspacing=0 cellpadding=0>"+picImg+"</td></tr>";
  var storyRow = "<tr class='mobilepix-story'><td cellspacing=0 cellpadding=0>"+dataObj['story']+"</td></tr>";
  var div_elem = $("<table class='mobilepix-pic' cellspacing=0 cellpadding=0><thead></thead><tbody>"+picRow+storyRow+"</tbody></table>");
  return div_elem;
};

var onSuccess = function(data){
  var container = $('#mobilepix-container');
  for (var i in data) {
    var div_elem = makePicTable(data[i]);
    container.append(div_elem);
  }
};

$.getJSON('/mobile_pix/gallery.json', null, onSuccess);
