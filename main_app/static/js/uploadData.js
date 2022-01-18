function uploadData() {
    var numData = document.getElementById('numData').value;
    localStorage.setItem('numData', numData);
}

function uploadTREC() {

}

function clean() {
    localStorage.clear();
}