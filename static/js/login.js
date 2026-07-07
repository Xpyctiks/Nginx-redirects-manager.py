function showLoading() {
  document.getElementById("spinner").style.visibility = "visible";
}

function deleteLoading() {
  document.getElementById("spinnerLoading").className = "spinner-border text-danger";
  document.getElementById("spinnerLoading").style.visibility = "visible";
}

document.addEventListener("DOMContentLoaded", function () {
  const modalElement = document.getElementById("myModal");
  if (modalElement) {
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
  }
});
