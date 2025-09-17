document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("query-form");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = document.getElementById("query").value;
        const response = await fetch("/ask", {
            method: "POST",
            body: new URLSearchParams({ query })
        });
        const data = await response.json();
        document.getElementById("answer").innerText = data.answer;
    });
});
