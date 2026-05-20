const loginForm = document.getElementById("loginForm");
const errorText = document.getElementById("errorText");

loginForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    const formData = new FormData();

    formData.append(
        "username",
        document.getElementById("username").value
    );

    formData.append(
        "password",
        document.getElementById("password").value
    );

    const response = await fetch("/login", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        errorText.innerText =
            data.detail || "Login failed";
        return;
    }

    localStorage.setItem(
        "token",
        data.access_token
    );

    window.location.href = "/dashboard";
});