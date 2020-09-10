document.addEventListener('DOMContentLoaded', () => {
    function handle_event_wrapper(show, hide) {
        const handle_event = (e) => {
            if (show()) {
                hide();
            }
            e.stopPropagation();
        }

        return handle_event;
    }

    let elements = document.getElementsByClassName("dropdown");

    for (let element of elements) {

        // We shouldn't handle hoverable menues
        if (element.classList.contains("is-hoverable")) {
            continue;
        }

        const show = () => {
            if (element.classList.contains("is-active")) {
                return true;
            }
            element.classList.add("is-active");
            return false;
        }

        const hide = () => {
            element.classList.remove("is-active");
        }

        element.addEventListener("click", handle_event_wrapper(show, hide));
        document.body.addEventListener("click", hide);
    }
});
