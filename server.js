const express = require("express");
const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const session = require("express-session");
const MongoStore = require("connect-mongo");
const path = require("path");

const app = express();

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Sessions
app.use(
  session({
    secret: "supersecretkey",
    resave: false,
    saveUninitialized: false,
    store: MongoStore.create({
      mongoUrl: "mongodb://localhost:27017/phillycrimewatch", 
      dbName: "phillycrimewatch",
      collectionName: "sessions"
    }),
  })
);

// MongoDB Connection
mongoose
  .connect("mongodb://localhost:27017/phillycrimewatch")  // Changed from "mongodb://localhost:27017/" to include the database name
  .then(() => console.log("MongoDB connected"))
  .catch((err) => console.log(err));

// User Schema
const UserSchema = new mongoose.Schema({
  name: String,
  email: { type: String, unique: true },
  password: String,
});

const User = mongoose.model("User", UserSchema);

// Signup Route
app.post("/signup", async (req, res) => {
  const { name, email, password } = req.body;

  const hashed = await bcrypt.hash(password, 10);

  try {
    await User.create({ name, email, password: hashed });
    res.redirect("login.html");
  } catch (err) {
    res.send("Error: Email already exists");
  }
});

// Login Route
app.post("/login", async (req, res) => {
  const { email, password } = req.body;

  const user = await User.findOne({ email });

  if (!user) return res.send("User not found");

  const match = await bcrypt.compare(password, user.password);

  if (!match) return res.send("Incorrect password");

  req.session.userId = user._id;
  res.redirect("index.html");
});

// Protected Dashboard
app.get("/dashboard", async (req, res) => {
  if (!req.session.userId) return res.redirect("/login.html");

  const user = await User.findById(req.session.userId);

  res.send(`<h1>Welcome, ${user.name}</h1>`);
});

// Logout
app.get("/logout", (req, res) => {
  req.session.destroy(() => {
    res.redirect("login.html");
  });
});

// Static files
app.use(express.static(path.join(__dirname, "HTML")));

app.listen(3000, () => console.log("Server running on port 3000"));
