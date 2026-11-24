document.querySelectorAll("input[data-digits-only]").forEach((input) => {
  input.addEventListener("beforeinput", (event) => {
    if (event.inputType.startsWith("insert") && event.data && /[^0-9]/.test(event.data)) {
      event.preventDefault();
    }
  });

  input.addEventListener("input", () => {
    const position = input.selectionStart ?? input.value.length;
    const value = input.value;
    const digits = value.replace(/[^0-9]/g, "");

    if (digits !== value) {
      const cursor = value.slice(0, position).replace(/[^0-9]/g, "").length;
      input.value = digits;
      input.setSelectionRange(cursor, cursor);
    }
  });
});
