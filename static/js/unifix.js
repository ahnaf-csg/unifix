// UniFix helper scripts (docs/05 §2): small helpers only, no frameworks.
// Every page works without JavaScript; these only add hints. The server
// always checks files itself (VR-07).

document.addEventListener("DOMContentLoaded", function () {
  // S-02 step 2: list the chosen files with their sizes, warn early about
  // the VR-07 limits, and offer "Clear files" (a file input cannot drop single files).
  var MAX_SIZE = 15 * 1024 * 1024;
  var MAX_FILES = 5;

  document.querySelectorAll("input[type=file][data-file-list]").forEach(function (input) {
    var list = document.getElementById(input.dataset.fileList);
    var clear = document.querySelector("[data-clear-files='" + input.id + "']");

    function show() {
      list.innerHTML = "";
      Array.prototype.forEach.call(input.files, function (file) {
        var item = document.createElement("li");
        item.textContent = file.name + " · " + (file.size / 1024 / 1024).toFixed(1) + " MB";
        if (file.size > MAX_SIZE) {
          var warning = document.createElement("span");
          warning.className = "form-error";
          warning.textContent = "larger than 15 MB";
          item.appendChild(warning);
        }
        list.appendChild(item);
      });
      if (input.files.length > MAX_FILES) {
        var tooMany = document.createElement("li");
        tooMany.className = "form-error";
        tooMany.textContent = "You can attach at most " + MAX_FILES + " files.";
        list.appendChild(tooMany);
      }
      list.hidden = clear.hidden = input.files.length === 0;
    }

    input.addEventListener("change", show);
    clear.addEventListener("click", function (event) {
      event.preventDefault();
      input.value = "";
      show();
    });
  });

  // S-02 step 1: "What happens next" names the department of the chosen
  // category (the department is the <optgroup> label).
  var category = document.querySelector("select[name=category]");
  var departmentName = document.querySelector("[data-department-name]");
  if (category && departmentName) {
    var initialText = departmentName.textContent;
    category.addEventListener("change", function () {
      var option = category.options[category.selectedIndex];
      var group = option && option.parentElement;
      departmentName.textContent = group && group.label ? group.label : initialText;
    });
  }
});
