// Makes bulma-collapsible work out of the box
// Needs the bulma-collapsible extension enabled to work
// Documentation: https://bulma-collapsible.netlify.app/javascript/

window.addEventListener("load", () => {
  if (typeof bulmaCollapsible === "undefined") {
    throw new Error(
      "The bulma-collapsible extension is not enabled, enable it to use the runner."
    );
  }
  bulmaCollapsible.attach();
});
