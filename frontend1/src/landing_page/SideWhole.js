// Sidebar.jsx
import React, { useState, useEffect } from 'react';
import './styles.css'; 
import { Link, useLocation } from 'react-router-dom';

const SideWhole = () => {
    const [isNavbarVisible, setIsNavbarVisible] = useState(false);
    const [activeLink, setActiveLink] = useState('dashboard');
    const location = useLocation(); // Get the current path from the router

    // Toggle sidebar visibility
    const toggleNavbar = () => {
        setIsNavbarVisible(!isNavbarVisible);
    };

    // Set active link based on the current URL path
    useEffect(() => {
        const currentPath = location.pathname;

        if (currentPath.includes('/dashwhole')) {
            setActiveLink('dashboard');
        } else if (currentPath.includes('/rec')) {
            setActiveLink('users');
        } else if (currentPath.includes('/home')) {
            setActiveLink('home');
        } else if (currentPath.includes('/login_auth')) {
            setActiveLink('signout');
        }
    }, [location]);

    // This function will set the active link when a link is clicked
    const handleLinkClick = (link) => {
        setActiveLink(link);
    };

    return (
        <div className="side-bar">
            <div id="body-pd">
                <header className={`header ${isNavbarVisible ? 'body-pd' : ''}`} id="header">
                    <div className="header_toggle" onClick={toggleNavbar}>
                        <i className={`bx bx-menu ${isNavbarVisible ? 'bx-x' : ''}`} id="header-toggle"></i>
                    </div>
                    <div>
                        <h1 className='nirvana' style={{ marginTop: "12px" }}>
                            NIRVANA <span style={{ color: "blue" }}>-</span> <span className='healthchain'>HealthChain</span>
                        </h1>
                    </div>
                    <div className="header_img">
                        <img src="https://i.imgur.com/hczKIze.jpg" alt="Profile" />
                    </div>
                </header>
                <div className={`l-navbar ${isNavbarVisible ? 'show' : ''}`} id="nav-bar">
                    <nav className="nav">
                        <div>
                            <Link
                                className={`nav_logo ${activeLink === 'home' ? 'active' : ''}`}
                                to="/home"
                                onClick={() => handleLinkClick('home')}
                            >
                                <i className='bx bx-layer nav_logo-icon dash' style={{ fontSize: "28px" }}></i>
                                <span className="nav_logo-name">
                                    <span style={{ color: "orange" }}>Nirvana</span>
                                    <br></br>
                                    <span style={{ color: "#87f167" }}>HealthChain</span>
                                </span>
                            </Link>
                            <div className="nav_list">
                                <Link
                                    className={`nav_link ${activeLink === 'dashboard' ? 'active' : ''}`}
                                    onClick={() => handleLinkClick('dashboard')}
                                    to="/dashwhole"
                                >
                                    <i className='bx bx-grid-alt nav_icon' style={{ fontSize: "25px" }}></i>
                                    <span className="nav_name">Dashboard</span>
                                </Link>

                                <Link
                                    className={`nav_link ${activeLink === 'users' ? 'active' : ''}`}
                                    onClick={() => handleLinkClick('users')}
                                    to="/rec"
                                >
                                    <i className="fa-duotone fa-solid fa-cart-shopping nav_icon"></i>
                                    <span className="nav_name">Receive</span>
                                </Link>
                            </div>
                        </div>
                        <Link
                            to="/login_auth"
                            className={`nav_link ${activeLink === 'signout' ? 'active' : ''}`}
                            onClick={() => handleLinkClick('signout')}
                        >
                            <i className='bx bx-log-out nav_icon' style={{ fontSize: "25px" }}></i>
                            <span className="nav_name">SignOut</span>
                        </Link>
                    </nav>
                </div>
            </div>
        </div>
    );
};

export default SideWhole;
