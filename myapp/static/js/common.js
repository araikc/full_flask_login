function copyToClip() {
  var copyText = document.getElementById("js-copyInput");
  copyText.select();
  document.execCommand("Copy");
}