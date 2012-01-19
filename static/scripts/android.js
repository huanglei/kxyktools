function delApp(key) {
	var appkey = encodeURIComponent(key);
	$.post('/admin/android/del', {
		'appkey' : appkey
	}, function(data, textStatus) {
		if(data.result == 'True') {
			alert('delete ok');
		} else {
			alert('delete error:' + data.result);
		}
	}, 'json');
}
function initApps(){
	$.post('/admin/android/init',{},function(){
		alert('init ok');
	});
}
