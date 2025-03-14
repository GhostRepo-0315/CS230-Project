// import React, { useState } from "react";

// // Define a list of predefined usernames and passwords for authentication
// const fakeUsers = [
//   { username: "admin", password: "1234" },
//   { username: "user1", password: "password" },
//   { username: "test", password: "test123" },
// ];

// // Define the Login component with a prop `onLogin` to update the logged-in user state
// const Login: React.FC<{ onLogin: (username: string) => void }> = ({ onLogin }) => {
//   // State to store the input values from the user
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState(""); // State to store login error messages

//   /**
//    * Handles the login process.
//    * Checks if the entered username and password match a predefined user.
//    * If successful, calls `onLogin` to set the logged-in user.
//    * Otherwise, displays an error message.
//    */
//   const handleLogin = () => {
//     // Check if the user exists in the predefined users list
//     const user = fakeUsers.find((u) => u.username === username && u.password === password);
    
//     if (user) {
//       // If user exists, call the onLogin function to update the App state
//       onLogin(username);
//     } else {
//       // If credentials don't match, show an error message
//       setError("Invalid username or password!");
//     }
//   };

//   return (
//     <div>
//       <h2>Login</h2>
      
//       {/* Display error message if login fails */}
//       {error && <p style={{ color: "red" }}>{error}</p>}

//       {/* Input field for the username */}
//       <input
//         type="text"
//         placeholder="Username"
//         value={username}
//         onChange={(e) => setUsername(e.target.value)} // Update state when input changes
//       />

//       {/* Input field for the password */}
//       <input
//         type="password"
//         placeholder="Password"
//         value={password}
//         onChange={(e) => setPassword(e.target.value)} // Update state when input changes
//       />

//       {/* Button to submit the login form */}
//       <button onClick={handleLogin}>Login</button>
//     </div>
//   );
// };

// export default Login; // Export the component for use in other files
//version with backend


import React, { useState } from "react";
import axios from "axios"; // Import axios to make HTTP requests

const Login: React.FC<{ onLogin: (username: string) => void }> = ({ onLogin }) => {
  // State to track user input
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(""); // State to handle errors
  const [loading, setLoading] = useState(false); // State for loading effect

  /**
   * Handles login by sending credentials to the backend.
   * This function simulates an API request using axios.
   */
  const handleLogin = async () => {
    if (!username || !password) {
      setError("Please enter both username and password.");
      return;
    }

    setLoading(true); // Show loading while waiting for a response
    setError(""); // Clear any previous errors

    try {
      // Simulating a backend API request
      const response = await axios.post("https://jsonplaceholder.typicode.com/posts", {
        username,
        password,
      });

      console.log("API Response:", response.data);

      // Fake success check (Normally, backend will validate and return a token)
      if (response.status === 201) {
        onLogin(username); // Call onLogin to update App state
      } else {
        setError("Invalid username or password.");
      }
    } catch (err) {
      setError("Failed to connect to the server. Please try again.");
    } finally {
      setLoading(false); // Stop loading
    }
  };

  return (
    <div>
      <h2>Login</h2>

      {/* Display error messages */}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* Input field for username */}
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      {/* Input field for password */}
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      {/* Button to submit login request */}
      <button onClick={handleLogin} disabled={loading}>
        {loading ? "Logging in..." : "Login"}
      </button>
    </div>
  );
};

export default Login; // Export component for use in App.tsx
