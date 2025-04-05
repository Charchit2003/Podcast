# Express MongoDB API

This project is a simple Node.js Express backend that integrates MongoDB using Mongoose. It provides basic APIs for user management, including creating, fetching, updating, and deleting users.

## Project Structure

```
express-mongo-api
├── src
│   ├── models
│   │   └── User.js
│   ├── routes
│   │   └── api.js
│   ├── config
│   │   └── db.js
│   └── app.js
├── package.json
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd express-mongo-api
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up MongoDB:**
   Ensure you have a MongoDB instance running. You can use a local instance or a cloud service like MongoDB Atlas.

4. **Configure the database connection:**
   Update the connection string in `src/config/db.js` to point to your MongoDB instance.

5. **Run the application:**
   ```bash
   npm start
   ```

   The server will start on port 8080.

## API Endpoints

- **POST /api/users**: Create a new user
- **GET /api/users**: Fetch all users
- **GET /api/users/:id**: Fetch a user by ID
- **PUT /api/users/:id**: Update a user by ID
- **DELETE /api/users/:id**: Delete a user by ID

## License

This project is licensed under the MIT License.