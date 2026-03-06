import os
import re

# Base path to all HTML files
html_dir = r"c:\Users\JPMR2\OneDrive\Documents\CI 102 Drexel\crime_dashboard\HTML"

# The standard navigation block we want everywhere
standard_nav = """    <!-- Nav -->
    <nav id="nav">
      <ul class="links">
        <li><a href="index.html">Home</a></li>
        <li><a href="map.html">Crime Map</a></li>
        <li><a href="data.html">Statistics</a></li>
        <li><a href="reports.html">Reports</a></li>
        <li><a href="about.html">About Us</a></li>
        <li><a href="contact.html">Contact</a></li>
        
        <!-- Auth Links -->
        <li class="auth-guest"><a href="signup.html" class="nav-btn">Sign Up</a></li>
        <li class="auth-guest"><a href="login.html" class="nav-btn-outline">Login</a></li>
        <li class="auth-user" style="display: none;"><a href="profile.html">Profile</a></li>
        <li class="auth-user" style="display: none;"><a href="#" class="auth-nav-logout nav-btn-outline">Logout</a></li>
      </ul>
      <ul class="icons">
        <li>
          <a href="https://gitlab.com/yourusername/phillycrimewatch" class="icon brands fa-gitlab">
            <span class="label">GitLab</span>
          </a>
        </li>
      </ul>
    </nav>"""

# Regular expression to find any existing <nav id="nav">...</nav> block
nav_regex = re.compile(r'(\s*<!--\s*Nav\s*-->\s*)?<nav id="nav">.*?</nav>', re.DOTALL | re.IGNORECASE)

# Iterate over all HTML files in the directory
for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(html_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if a nav block exists
        if nav_regex.search(content):
            # Replace the old nav block with the standard one
            new_content = nav_regex.sub(standard_nav, content)
            
            # Ensure nav-auth.js is included
            if "assets/js/nav-auth.js" not in new_content:
                # Add it right before </body>
                new_content = re.sub(r'(</body>)', r'  <script src="assets/js/nav-auth.js"></script>\n\1', new_content, flags=re.IGNORECASE)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated navigation bar in: {filename}")
        else:
            print(f"Skipped {filename}: No <nav id='nav'> found.")

print("Finished standardizing HTML navigation bars.")
