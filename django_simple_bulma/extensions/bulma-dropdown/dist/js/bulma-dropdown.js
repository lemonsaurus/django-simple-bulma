(function() {
    window.dropdowns = {};

    function handle_event(e) {
        show();

        function clickEvent() {
            hide();
            document.body.removeEventListener("click", clickEvent);
        };

        document.body.addEventListener("click", clickEvent);
        e.stopPropagation();
    }

    let elements = document.getElementsByClassName("dropdown");

    for (let element of elements) {

        // We shouldn't handle hoverable menues
        if (element.classList.contains("is-hoverable")) {
            continue;
        }

        let menu_element = element.getElementsByClassName("dropdown-menu")[0];

        function show() {
            element.classList.add("is-active");
        }

        function hide() {
            element.classList.remove("is-active");
        }

        element.addEventListener("click", handle_event);

        window.dropdowns[menu_element.id] = element;
    }
})();
