const API_BASE = "http://127.0.0.1:8000";

const form = document.getElementById("loginForm");
const message = document.getElementById("message");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    message.innerHTML = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {

        const response = await fetch(`${API_BASE}/login`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email,
                password
            })

        });

        const data = await response.json();

        if (!response.ok) {

            message.innerHTML =
                `<div class="alert alert-danger">${data.detail}</div>`;

            return;
        }

        // Save JWT token
        auth.saveToken(data.access_token);

        message.innerHTML =
            '<div class="alert alert-success">Login successful!</div>';

        setTimeout(() => {

            window.location.href = "analysis.html";

        }, 800);

    } catch (error) {

        console.error(error);

        message.innerHTML =
            '<div class="alert alert-danger">Cannot connect to backend.</div>';

    }

});