window.onload = function() {
    // Apply this to all upload fields
    const upload_fields = document.querySelectorAll(".file");
    for (let i = 0; i < upload_fields.length; i++) {
        let input = upload_fields[i].querySelector(".file-input");
        let filename = upload_fields[i].querySelector(".file-name");

        input.onchange = function() {
            filename.textContent = input.files[0].name;
        }
    }
};
