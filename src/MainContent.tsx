import React from "react";

interface User {
  name: string;
  email: string;
  joined: string;
}

const users: User[] = [
  { name: "Florence Shaw", email: "florence@example.com", joined: "Mar 4, 2024" },
  { name: "Amelie Laurent", email: "amelie@example.com", joined: "Mar 5, 2024" },
  { name: "Sienna May", email: "sienna@example.com", joined: "Mar 7, 2024" },
];

const MainContent: React.FC = () => {
  return (
    <main className="main-content">
      <div className="main-content-header">
        <h1>User Management</h1>
        <button className="add-user-btn">Add User</button>
      </div>
      <div className="table-container">
        <table className="user-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Joined</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user, idx) => (
              <tr key={idx}>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.joined}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
};

export default MainContent;