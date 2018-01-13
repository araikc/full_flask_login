function copyToClip() {
  var copyText = document.getElementById("js-copyInput");
  copyText.select();
  document.execCommand("Copy");
}

function preloader(){
    document.getElementById("loading").style.display = "none";
    document.getElementById("content").style.display = "block";
}//preloader
window.onload = preloader;
