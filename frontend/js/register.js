const API_BASE = window.API_BASE;

const form = document.getElementById("registerForm");
const message = document.getElementById("message");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    message.innerHTML = "";

    if (password !== confirmPassword) {
        message.innerHTML =
            '<div class="alert alert-danger">Passwords do not match.</div>';
        return;
    }

    try {

        const response = await fetch(`${API_BASE}/register`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username,
                email,
                password
            })

        });

        const data = await response.json();

        if (response.ok) {

            message.innerHTML =
                '<div class="alert alert-success">Registration successful! Redirecting to login...</div>';

            setTimeout(() => {
                window.location.href = "login.html";
            }, 1500);

        } else {

            message.innerHTML =
                `<div class="alert alert-danger">${data.detail}</div>`;
        }

    } catch (error) {

        console.error(error);

        message.innerHTML =
            '<div class="alert alert-danger">Cannot connect to backend.</div>';
    }

});