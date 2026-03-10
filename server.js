const express = require("express");
const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const session = require("express-session");
const MongoStore = require("connect-mongo");
const path = require("path");

const app = express();

// Use the same connection string for both mongoose and MongoStore
const MONGODB_URI = "mongodb+srv://mailemail761_db_user:hNHbde9zVXfSpXZz@cluster0.hhdwin9.mongodb.net/phillycrimewatch?retryWrites=true&w=majority";

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(
  session({
    secret: "supersecretkey",
    resave: false,
    saveUninitialized: false,
    store: MongoStore.create({
      mongoUrl: MONGODB_URI,
      collectionName: "sessions",
      dbName: "phillycrimewatch" // Explicitly specify database name
    }),
  })
);

mongoose
  .connect(MONGODB_URI)
  .then(() => {
    console.log("MongoDB connected successfully");
    console.log("Database: phillycrimewatch");
    console.log("Collections will be created automatically when data is inserted");
  })
  .catch((err) => {
    console.error("MongoDB connection error:", err);
  });

const UserSchema = new mongoose.Schema({
  name: String,
  email: { type: String, unique: true },
  password: String,
  phone: { type: String, default: "" },
  preferences: {
    email_enabled: { type: Boolean, default: true },
    sms_enabled: { type: Boolean, default: false }
  },
  saved_locations: [{
    name: String,
    address: String
  }]
});

const User = mongoose.model("User", UserSchema);

app.post("/signup", async (req, res) => {
  try {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
      return res.status(400).send("All fields are required");
    }

    const hashed = await bcrypt.hash(password, 10);

    const user = await User.create({ name, email, password: hashed });
    console.log("User created successfully:", { id: user._id, email: user.email });

    // Ensure response hasn't been sent
    if (!res.headersSent) {
      res.redirect(302, "login.html");
    }
  } catch (err) {
    if (err.code === 11000) {
      if (!res.headersSent) {
        res.status(400).send("Error: Email already exists");
      }
    } else {
      console.error("Signup error:", err);
      if (!res.headersSent) {
        res.status(500).send("Internal server error: " + err.message);
      }
    }
  }
});

app.post("/login", async (req, res) => {
  try {
    console.log("Login attempt received:", { email: req.body.email });
    const { email, password } = req.body;

    if (!email || !password) {
      console.log("Missing email or password");
      return res.status(400).send("Email and password are required");
    }

    const user = await User.findOne({ email });

    if (!user) {
      console.log("User not found:", email);
      return res.status(401).send("User not found");
    }

    const match = await bcrypt.compare(password, user.password);

    if (!match) {
      console.log("Password mismatch for:", email);
      return res.status(401).send("Incorrect password");
    }

    // Set session data
    req.session.userId = user._id;
    console.log("User logged in successfully:", { userId: user._id, email: user.email });
    console.log("Redirecting to /index.html");

    // Redirect immediately - express-session will save automatically
    return res.redirect("index.html");
  } catch (err) {
    console.error("Login error:", err);
    if (!res.headersSent) {
      return res.status(500).send("Internal server error: " + err.message);
    }
  }
});

// --- Profile Routes ---
app.get("/api/profile", async (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  try {
    const user = await User.findById(req.session.userId, "-password");
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }
    res.json(user);
  } catch (err) {
    console.error("Profile fetch error:", err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.post("/api/profile", async (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  try {
    const { email, phone, email_enabled, sms_enabled } = req.body;

    // Check if the new email is already taken by someone else
    if (email) {
      const existingEmail = await User.findOne({ email, _id: { $ne: req.session.userId } });
      if (existingEmail) {
        return res.status(400).json({ error: "Email already in use" });
      }
    }

    const updatedUser = await User.findByIdAndUpdate(
      req.session.userId,
      {
        $set: {
          email,
          phone: phone || "",
          "preferences.email_enabled": email_enabled,
          "preferences.sms_enabled": sms_enabled
        }
      },
      { new: true, runValidators: true }
    ).select("-password");

    res.json({ message: "Profile updated successfully", user: updatedUser });
  } catch (err) {
    console.error("Profile update error:", err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

// Add a saved location
app.post("/api/profile/locations", async (req, res) => {
  if (!req.session.userId) return res.status(401).json({ error: "Unauthorized" });

  try {
    const { name, address } = req.body;
    if (!name || !address) return res.status(400).json({ error: "Name and address required" });

    const user = await User.findByIdAndUpdate(
      req.session.userId,
      { $push: { saved_locations: { name, address } } },
      { new: true }
    ).select("-password");

    res.json({ message: "Location saved successfully", user });
  } catch (err) {
    console.error("Location save error:", err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

// Delete a saved location
app.delete("/api/profile/locations/:locationId", async (req, res) => {
  if (!req.session.userId) return res.status(401).json({ error: "Unauthorized" });

  try {
    const user = await User.findByIdAndUpdate(
      req.session.userId,
      { $pull: { saved_locations: { _id: req.params.locationId } } },
      { new: true }
    ).select("-password");

    res.json({ message: "Location deleted successfully", user });
  } catch (err) {
    console.error("Location delete error:", err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

// Logout route
app.post("/api/logout", (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      console.error("Logout error:", err);
      return res.status(500).json({ error: "Could not log out" });
    }
    res.clearCookie("connect.sid"); // The default name of the express-session cookie
    res.json({ message: "Logged out successfully" });
  });
});

// Auth status route
app.get("/api/auth/status", (req, res) => {
  if (req.session.userId) {
    res.json({ loggedIn: true });
  } else {
    res.json({ loggedIn: false });
  }
});

// Test route
app.get("/test", (req, res) => {
  res.send("Server is working! Routes are functioning.");
});

// Test redirect route
app.get("/test-redirect", (req, res) => {
  res.redirect("index.html");
});

// Root route - redirect to index.html
app.get("/", (req, res) => {
  res.redirect("index.html");
});

// Contact Form Route
app.post("/api/contact", (req, res) => {
  const { name, email, message } = req.body;

  if (!name || !email || !message) {
    return res.status(400).json({ error: "All fields are required" });
  }

  // In a real application, you would send an email here.
  // We'll simulate a successful message send.
  console.log("Contact form filled by:", email, "Message:", message);

  res.json({ message: "Thank you for reaching out! Your message has been sent." });
});

// Explicit routes for HTML files
app.get("/index.html", (req, res, next) => {
  const filePath = path.join(__dirname, "HTML", "index.html");
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error("Error sending index.html:", err);
      next(err);
    }
  });
});

app.get("/login.html", (req, res, next) => {
  const filePath = path.join(__dirname, "HTML", "login.html");
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error("Error sending login.html:", err);
      next(err);
    }
  });
});

app.get("/signup.html", (req, res, next) => {
  const filePath = path.join(__dirname, "HTML", "signup.html");
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error("Error sending signup.html:", err);
      next(err);
    }
  });
});

app.get("/profile.html", (req, res, next) => {
  const filePath = path.join(__dirname, "HTML", "profile.html");
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error("Error sending profile.html:", err);
      next(err);
    }
  });
});

app.get("/contact.html", (req, res, next) => {
  const filePath = path.join(__dirname, "HTML", "contact.html");
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error("Error sending contact.html:", err);
      next(err);
    }
  });
});

app.get("/reports.html", (req, res, next) => {
  const filePath = path.join(__dirname, "HTML", "reports.html");
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error("Error sending reports.html:", err);
      next(err);
    }
  });
});

// Serve static files from HTML directory (for assets, images, etc.)
app.use(express.static(path.join(__dirname, "HTML")));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error("Server error:", err);
  if (!res.headersSent) {
    res.status(500).send("Server error: " + err.message);
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Access the app at http://localhost:${PORT}`);
});
