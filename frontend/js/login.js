// Each form sends its fields as JSON to its data-endpoint and shows the reply.
const output = document.getElementById("output");

for (const form of document.querySelectorAll("form[data-endpoint]")) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const method = form.dataset.method ?? "POST";
    const fields = Object.fromEntries(new FormData(form));
    try {
      const res = await fetch(form.dataset.endpoint, {
        method,
        headers: { "content-type": "application/json" },
        body: method === "GET" ? undefined : JSON.stringify(fields),
      });
      const text = await res.text();
      output.textContent = `${res.status} ${res.statusText}\n${text}`;
    } catch (err) {
      output.textContent = `error: ${err.message}`;
    }
  });
}
