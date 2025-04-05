const express = require('express');
const router = express.Router();

// Define routes
router.get('/', (req, res) => {
    res.json({ message: 'Welcome to the API' });
});

// User routes
router.get('/user/:id', (req, res) => {
    // Logic to fetch a user by ID
});

router.post('/user', (req, res) => {
    // Logic to create a new user
});

router.put('/user/:id', (req, res) => {
    // Logic to update user information
});

router.delete('/user/:id', (req, res) => {
    // Logic to delete a user
});

module.exports = router;  // Export only the router