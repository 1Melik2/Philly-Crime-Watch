document.addEventListener("DOMContentLoaded", async () => {
    // We must wait slightly for main.js to clone the nav for mobile
    setTimeout(async () => {
        // Find both the desktop and mobile navigation lists
        const navLists = document.querySelectorAll("#nav .links, #navPanel nav .links");

        // Check authentication status
        try {
            const response = await fetch('/api/auth/status');
            const authStat = await response.json();
            const isLoggedIn = authStat.loggedIn;

            const guestLinks = document.querySelectorAll('.auth-guest');
            const userLinks = document.querySelectorAll('.auth-user');

            if (isLoggedIn) {
                // Hide Guest Links (Login, Signup)
                guestLinks.forEach(el => el.style.display = 'none');

                // Show User Links (Profile, Logout)
                userLinks.forEach(el => el.style.display = 'block');

                // Attach Logout Event Listeners
                document.querySelectorAll('.auth-nav-logout').forEach(btn => {
                    // Prevent duplicate listeners
                    const newBtn = btn.cloneNode(true);
                    btn.parentNode.replaceChild(newBtn, btn);

                    newBtn.addEventListener('click', async (e) => {
                        e.preventDefault();
                        try {
                            const res = await fetch('/api/logout', { method: 'POST' });
                            if (res.ok) window.location.href = 'index.html';
                        } catch (err) {
                            console.error("Logout failed:", err);
                        }
                    });
                });

            } else {
                // Not Logged In
                // Show Guest Links (Login, Signup)
                guestLinks.forEach(el => el.style.display = 'block');

                // Hide User Links (Profile, Logout)
                userLinks.forEach(el => el.style.display = 'none');

                // Current page path
                const currentPath = window.location.pathname.split("/").pop() || "index.html";

                // If the user happens to be on /profile.html while logged out, kick them out
                if (currentPath === "profile.html") {
                    window.location.href = "login.html";
                }
            }

            // Set active class for the current page
            const currentPath = window.location.pathname.split("/").pop() || "index.html";
            navLists.forEach(navList => {
                navList.querySelectorAll('li').forEach(li => {
                    const a = li.querySelector('a');
                    if (a && a.getAttribute('href') === currentPath) {
                        li.classList.add('active');
                    } else if (a && a.getAttribute('href') !== '#') {
                        li.classList.remove('active');
                    }
                });
            });

        } catch (err) {
            console.error("Error checking auth status:", err);
        }
    }, 150); // 150ms delay to let main.js run first
});
