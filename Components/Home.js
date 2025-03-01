import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home">
      <div className="hero">
        <h1>Welcome to JWS Water Service</h1>
        <p>Your trusted partner for clean and reliable water services.</p>
        <Link to="/login" className="cta-button">Get Started</Link>
      </div>

      <div className="portals">
        <div className="card">
          <h2>Driver Portal</h2>
          <p>Manage your assigned water stations and mark them as complete.</p>
          <Link to="/driver" className="card-button">Go to Driver Portal</Link>
        </div>
        <div className="card">
          <h2>Dealer Portal</h2>
          <p>Add and manage deals with customers.</p>
          <Link to="/dealer" className="card-button">Go to Dealer Portal</Link>
        </div>
        <div className="card">
          <h2>Admin Portal</h2>
          <p>Manage water stations, users, and system settings.</p>
          <Link to="/admin" className="card-button">Go to Admin Portal</Link>
        </div>
      </div>
    </div>
  );
};

export default Home;