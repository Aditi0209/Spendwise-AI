const auth = {

    getToken() {
        return localStorage.getItem("access_token");
    },

    saveToken(token) {
        localStorage.setItem("access_token", token);
    },

    removeToken() {
        localStorage.removeItem("access_token");
    },

    authHeaders() {

        const token = this.getToken();

        return {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        };
    },

    requireLogin() {

        if (!this.getToken()) {
            window.location.href = "login.html";
        }
    },

    logout() {

    localStorage.clear();
    sessionStorage.clear();

    window.location.replace("login.html");
}
};

window.auth = auth;