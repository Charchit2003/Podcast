const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const apiRoutes = require('./routes/api');
const dbConfig = require('./config/db');

const app = express();
const PORT = 8080;

// Middleware
app.use(bodyParser.json());

// Database connection
// dbConfig();

// API routes
app.use('/api', apiRoutes);  // Using the router directly

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

module.exports = app;