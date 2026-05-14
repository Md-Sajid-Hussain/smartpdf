import { Link } from "react-router-dom";
import logo from "./mainlogo.png"; 

function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/" className="nav-logo-link">
          <img src={logo} alt="SmartPDF Logo" className="nav-logo" />
          <span className="brand-name">
            Smart<span className="brand-accent">PDF</span>
          </span>
        </Link>
      </div>

      <div className="nav-links">
        <Link to="/">
          <button className="nav-btn">Home</button>
        </Link>
      </div>
    </nav>
  );
}

export default Navbar;