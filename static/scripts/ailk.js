 function getData(){
	 $.post("/ailkajax", {shares:$('#shares').attr('value')}, function(msg) {
		rs = eval('('+msg+')'); 
		$('#ae-result-body .ae-table td:eq(2)').html(rs['ailkshares'])
		$('#ae-result-body .ae-table td:eq(3)').html(rs['money'])
	 })
 }