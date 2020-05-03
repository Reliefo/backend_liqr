import React from "react";
import { slide as Menu } from "react-burger-menu";
import location from "../assets/location.png";
import { ReactComponent as SearchSVG } from "assets/searchIcon.svg";
import login from "../assets/login.png";
import notifications from "../assets/notifications.png";
import previousVisits from "../assets/previousVisits.png";
import settings from "../assets/settings.png";
import tableChange from "../assets/tableChange.png";
import * as TYPES from "Store/actionTypes.js";
import { StoreContext } from "Store";

export default props => {
  const [showCollapse, setShowCollapse] = React.useState(false);
  const sideDrawerInner = React.useRef();
  const menuRef = React.useRef();
  const inputNode = React.useRef();

  const {
    dispatch,
    state: { searchClicked, searchValue }
  } = React.useContext(StoreContext);

  const searchValueChange = ({ target: { value } }) => {
    dispatch({ type: TYPES.SET_GENERAL_DATA, payload: { searchValue: value } });
  };

  const searchIconClick = () => {
    inputNode.current.focus();
    dispatch({
      type: TYPES.SET_GENERAL_DATA,
      payload: { searchClicked: true }
    });
  };
  const closeSearchHndlr = () => {
    dispatch({
      type: TYPES.SET_GENERAL_DATA,
      payload: { searchClicked: false }
    });
  };
  return (
    <div>
        <SearchSVG onClick={searchIconClick} className="search-svg" />
        <div
          className="nav-search-bar"
          style={{ opacity: searchClicked ? 1 : 0 }}
        >
          <input
            ref={inputNode}
            value={searchValue}
            onChange={searchValueChange}
            type="text"
          />
          <span className="ml-3" onClick={closeSearchHndlr}>
            X
          </span>
        </div>
        <Menu disableAutoFocus width={"55%"}>
          <a className="menu-item shadow-menu" href="/login">
            <img className="navbar-menu-icon" src={login} alt="Login" /> Login/
            SignUp
          </a>
          <hr />

          <a className="menu-item" href="/menu">
            <img className="navbar-menu-icon" src={tableChange} alt="Login" />{" "}
            Table Change
          </a>

          <a className="menu-item" href="/menu">
            <img
              className="navbar-menu-icon"
              src={previousVisits}
              alt="Login"
            />{" "}
            Previous Visits
          </a>

          <a className="menu-item" href="/menu">
            <img className="navbar-menu-icon" src={location} alt="Login" />{" "}
            Dine-in History
          </a>

          <a className="menu-item" href="/menu">
            <img className="navbar-menu-icon" src={notifications} alt="Login" />{" "}
            Notifications
          </a>
          <hr className="navbar-menu-hr" />
          <hr className="navbar-menu-hr" />
          <hr className="navbar-menu-hr" />
          <hr className="navbar-menu-hr" />

          <a className="menu-item shadow-menu" href="/menu">
            <hr />
            <img className="navbar-menu-icon" src={settings} alt="Login" />{" "}
            Personal Settings
            <hr />
          </a>
        </Menu>
    </div>
  );
};
