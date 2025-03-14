// import React, { useState } from "react";
// import Login from "./components/Login"; // Import the Login component
// import FileUpload from "./components/FileUpload"; // Import the FileUpload component

// const App: React.FC = () => {
//   // State to track the logged-in user. Null means no one is logged in.
//   const [loggedInUser, setLoggedInUser] = useState<string | null>(null);

//   return (
//     <div>
//       {/* If a user is logged in, show the welcome message and file upload page */}
//       {loggedInUser ? (
//         <>
//           <h1>Welcome, {loggedInUser}!</h1>
//           <FileUpload />
//         </>
//       ) : (
//         // If no user is logged in, show the Login page
//         <Login onLogin={setLoggedInUser} />
//       )}
//     </div>
//   );
// };

// export default App; // Export the App component

import React from "react";
import FileUpload from "./components/FileUpload"; // Import the FileUpload component

const App: React.FC = () => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column", // Stack elements vertically
        alignItems: "center", // Center items horizontally
        justifyContent: "center", // Center items vertically
        height: "100vh", // Full height of the viewport
        textAlign: "center", // Center text
      }}
    >
      <h1>Distributed File Upload System</h1>
      <FileUpload />
    </div>
  );
};

export default App;
