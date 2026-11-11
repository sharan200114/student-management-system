
const API_BASE_URL = "http://127.0.0.1:5000/api";

const loginForm = document.getElementById("loginForm");
const loginButton = document.getElementById("loginButton");
const errorMessage = document.getElementById("errorMessage");

// If already logged in, open dashboard
if (sessionStorage.getItem("access_token")) {
    window.location.replace("index.html");
}

loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();

    const password = document.getElementById("password").value;

    errorMessage.textContent = "";

    loginButton.disabled = true;
    loginButton.textContent = "Signing in...";

    try {

        const response = await fetch(
            `${API_BASE_URL}/auth/login`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Login failed.");
        }

        // Store token for this browser session
        sessionStorage.setItem(
            "access_token",
            result.data.access_token
        );

        sessionStorage.setItem(
            "admin",
            JSON.stringify(result.data.admin)
        );

        // Navigate to dashboard
        window.location.replace("index.html");

    } catch (error) {

        errorMessage.textContent = error.message;

    } finally {

        loginButton.disabled = false;
        loginButton.textContent = "Login";

    }

});
