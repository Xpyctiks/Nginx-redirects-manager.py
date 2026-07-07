const checkboxes = document.querySelectorAll('.chk');
let lastChecked = null;
checkboxes.forEach(chk => {
  chk.addEventListener('click', function (e) {
    if (e.shiftKey && lastChecked) {
      let inRange = false;
      checkboxes.forEach(box => {
        if (box === this || box === lastChecked) {
          inRange = !inRange;
        }
        if (inRange) {
          box.checked = lastChecked.checked;
        }
        });
    }
    lastChecked = this;
  });
});

function checkAll(bx) {
  var cbs = document.getElementsByTagName('input');
  for(var i=0; i < cbs.length; i++) {
    if(cbs[i].type == 'checkbox') {
      cbs[i].checked = bx.checked;
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const modalElement = document.getElementById("myModal");
  if (modalElement) {
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
  }
});
