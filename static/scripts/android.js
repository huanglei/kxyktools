function delAppVersion(key) {
	var appkey = encodeURIComponent(key);
	$.post('/admin/android/del', {
		'appkey' : appkey
	}, function(data, textStatus) {
		if(data.result == 'True') {
			alert('delete ok');
			window.location.reload(); 
		} else {
			alert('delete error:' + data.result);
		}
	}, 'json');
}

function delApp(key) {
	var appkey = encodeURIComponent(key);
	$.post('/admin/android/delapp', {
		'appkey' : appkey
	}, function(data, textStatus) {
		if(data.result == 'True') {
			alert('delete ok');
			window.location.reload(); 
		} else {
			alert('delete error:' + data.result);
		}
	}, 'json');
}
function initApps(){
	$.post('/admin/android/init',{},function(){
		alert('init ok');
		window.location.reload();
	});
}
function showAppVersion(){
	appPackage = $('#appPackage').val();
	$.get('/android/'+appPackage,{},function(data){
		$('#appVersionCode').text(data);
	});
}
function downloadApp(){
	appPackage = $('#appPackage').val();
	window.location = '/download/android/'+appPackage+'/newest'
}
