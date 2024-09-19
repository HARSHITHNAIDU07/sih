const express = require('express');
const mysql = require('mysql2'); // Use mysql2 for better compatibility
const path = require('path'); // To handle file paths

const app = express();
const PORT = process.env.PORT || 5000;

// MySQL Connection
const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',        // Replace with your MySQL username
  password: '4343',        // Replace with your MySQL password
  database: 'login_system'
});

db.connect((err) => {
  if (err) throw err;
  console.log('MySQL Connected...');
});

// Middleware to parse JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public'))); // Make sure to have your index.html in the 'public' folder

// Register Route
app.post('/register', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Please provide both username and password' });
  }

  const queryCheck = 'SELECT * FROM users WHERE username = ?';
  db.query(queryCheck, [username], (err, result) => {
    if (err) throw err;

    if (result.length > 0) {
      return res.status(400).json({ error: 'User already exists' });
    } else {
      const queryInsert = 'INSERT INTO users (username, password) VALUES (?, ?)';
      db.query(queryInsert, [username, password], (err, result) => {
        if (err) throw err;
        res.status(201).json({ message: 'User registered successfully' });
      });
    }
  });
});

// Login Route
app.post('/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Please provide both username and password' });
  }

  const query = 'SELECT * FROM users WHERE username = ?';
  db.query(query, [username], (err, result) => {
    if (err) throw err;

    if (result.length === 0) {
      return res.status(400).json({ error: 'Invalid username or password' });
    }

    const user = result[0];
    if (user.password !== password) {
      return res.status(400).json({ error: 'Invalid username or password' });
    }

    res.json({ message: 'Login successful' });
  });
});

// Start the server
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
