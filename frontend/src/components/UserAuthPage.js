import React, { useState } from 'react';
import styled from 'styled-components';
import { registerUser, loginUser } from '../api';

const AuthContainer = styled.div`
  max-width: 400px;
  margin: 2rem auto;
  text-align: center;
`;

function UserAuthPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const newUser = await registerUser({ username, password, email });
      alert(`User created: ${newUser.username}`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Registration failed');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const result = await loginUser({ username, password });
      alert(result.message);
    } catch (err) {
      alert(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <AuthContainer>
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <button type="submit">Sign Up</button>
      </form>

      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Sign In</button>
      </form>
    </AuthContainer>
  );
}

export default UserAuthPage;