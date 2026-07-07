function showLoading() {
  const spinner = document.getElementById("spinnerLoading");
  if (spinner) spinner.style.visibility = "visible";
}

function syncSettings() {
  document.querySelectorAll("[id^='settings-']").forEach(src => {
    const i = src.id.split('-')[1];
    const target = document.getElementById(`value-${i}`);
    if (target) target.value = src.value;
  });
  showLoading();
}

document.querySelectorAll(".SaveSettings-btn").forEach(btn => {
  btn.addEventListener("click", e => {
    if (!confirm("Зберегти нові налаштування?")) e.preventDefault();
  });
});

document.querySelectorAll(".DeleteUser-btn").forEach(btn => {
  btn.addEventListener("click", e => {
    if (!confirm("Видалити користувача?")) e.preventDefault();
  });
});

document.querySelectorAll(".EditUser-btn").forEach(btn => {
  btn.addEventListener("click", e => {
    if (!confirm("Зберегти зміни користувача?")) e.preventDefault();
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const modalElement = document.getElementById("myModal");
  if (modalElement) {
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
  }
});
