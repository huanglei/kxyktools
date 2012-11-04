var Vote = {};

Vote.ListShow = (function() {
    var b, c, g, j;
    function a(k) {
        b = k.id;       
        g = k.percent;
        j = k.width;
        styleData = h();
        bindItems = d();
    }
    function d() {
        var o = [];
        m = $(".vote-item-wrap");
        for (var n = 0, k = m.length; n < k; n++) {
            o.push(m[n].children[1]);
        }
        
        return o
    }
    function h() {
        var o = [];
        var n = ["#5dbc5b", "#6c81b6", "#9eb5f0", "#a5cbd6", "#aee7f8", "#c2f263", "#d843b3", "#d8e929", "#e58652", "#e7ab6d", "#ee335f", "#fbe096", "#ffc535"];
        var q = n.slice();
        for (var p = 0, l = g.length; p < l; p++) {
            var k = Math.floor(Math.random() * q.length);
            o.push(q[k]);
            q.splice(k, 1);
            if (q.length == 0) {
                q = n.slice()
            }
        }
        return o
    }
    function f(l, k) {
        
        $(l.children[0]).css("background-color", k.color);
        $(l.children[1]).css({'background-color': k.color,'width': '0px'});
        $(l.children[2]).css("background-color", k.color);
    
    
    }
    function i() {
        var n = [];
        var l = [];
        for (var m = 0, k = g.length; m < k; m++) {
            f(bindItems[m], {color: styleData[m]});
            n.push(bindItems[m].children[1]);
            l.push(Math.round(g[m] * j))
        }
        e(n, 0, l, c)
    }
    function e(p, o, l, n) {        
         for (var r = 0, q = g.length; r < q; r++) {
             $(p[r]).animate({width: l[r]},"slow"); 
         }    
    }
    return {init: a,go: i}
})();