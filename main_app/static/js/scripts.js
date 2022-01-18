/*!
* Start Bootstrap - Landing Page v6.0.4 (https://startbootstrap.com/theme/landing-page)
* Copyright 2013-2021 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-landing-page/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project
function addQuery() {

}

function addOption(selector, value) {
    var objOption = document.createElement('option');
    objOption.text = value;
    objOption.value = value;
    selector.options.add(objOption);
}

function setBodypart() {
    var feature = document.getElementById("selectFeature");
    var feat = feature.options[feature.selectedIndex].value;
    var selector = document.querySelector("#selectBodypart");
    selector.options.length = 0;
    var selector2 = document.querySelector("#selectValue");
    selector2.options.length = 0;
    var dict = "{{ attributeSearchTable }}";
    var dict = dict.replace(/'/gi, '"');
    var jsondict = JSON.parse(dict);
    addOption(selector, "Choose");
    addOption(selector2, "Choose");
    for (var key in jsondict[feat]) {
        addOption(selector, key);
        console.log(key);
    }
}

function setValue() {
    var feature = document.getElementById("selectFeature");
    var feat = feature.options[feature.selectedIndex].value;
    var bodypart = document.getElementById("selectBodypart");
    var bp = bodypart.options[bodypart.selectedIndex].value;
    var selector = document.querySelector("#selectValue");
    selector.options.length = 0;
    var dict = "{{ attributeSearchTable }}";
    var dict = dict.replace(/'/gi, '"');
    var jsondict = JSON.parse(dict);
    addOption(selector, "Choose");
    console.log(feat);
    console.log(bp);
    console.log(jsondict[feat]);
    console.log(jsondict[feat][bp]);
    for (var value in jsondict[feat][bp]) {
        addOption(selector, jsondict[feat][bp][value]);
    }
}