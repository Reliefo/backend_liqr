import React from "react";
import home from "../assets/home.png";
import menu from "../assets/menu.png";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import cart from "../assets/cart.png";
import order from "../assets/order.png";
import { Link } from "react-router-dom";
import SocketContext from "../socket-context";
import { StoreContext } from "Store";
import { ReactComponent as WaterSVG } from "assets/water.svg";
import { ReactComponent as TissueSVG } from "assets/tissue.svg";
// import { ReactComponent as HelpSVG } from "assets/help.svg";
import { ReactComponent as DoubleArrow } from "assets/double-arrow.svg";
import * as TYPES from "Store/actionTypes.js";
const FooterNav = props => {
  const {
    state: {
      activeNav,
      tableId,
      activeData,
      placeOrderById,
      rawData: { food_menu = [] }
    },
    dispatch
  } = React.useContext(StoreContext);

  React.useEffect(() => {
    props.socket.off("assist").on("assist", ms => {
      const message = JSON.parse(ms);
      const { msg } = message;

      toast.info(msg, {
        position: "top-center",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined
      });
    });
  }, []);

  const fillSvg = name =>
    activeNav === name ? "icon-active" : "icon-inactive";
  const [deg, setDeg] = React.useState(0);
  const [state, setState] = React.useState({
    fabClicked: false,
    menuClick: false
  });

  const trfm = `rotate(${deg}deg)`;
  const revtrfm = `rotate(${-deg}deg)`;

  const FABClick = () => {
    console.log("clicked...");
    setState(state => ({ ...state, menuClick: false }));
    setState(state => ({ ...state, fabClicked: !state.fabClicked }));
  };

  const MenuClick = () => {
    console.log("clicked...");
    setState(state => ({ ...state, fabClicked: false }));
    setState(state => ({ ...state, menuClick: !state.menuClick }));
  };


  const sendAssistance = name => {
    const body = {
      table: localStorage.getItem('table_id'),
      user: localStorage.getItem('user_id'),
      assistance_type: name
    };
    props.socket.emit("assistance_requests", JSON.stringify(body));
  };
  return (
    <>
      <ToastContainer
        toastClassName="dark-toast"
        position="top-center"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
      <div className="footer-nav">
        {activeNav === "Menu" && (
          <div className="floating-container-menu">
            <div className="menu-button-footer" onClick={MenuClick}>
              <span>Menu</span>
            </div>
          </div>
        )}
        {state.menuClick && (
          <div className="floating-container-menu">
            <div
              className="floating-container menu-button"
              style={{ marginBottom: "2.5rem" }}
            >
              {activeData.map((item, idx) => {
                return (
                  <div key={idx}>
                    <a href={`#menu-${idx}`}> {item.name}</a>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        <div
          className={`floating-container ${
            state.fabClicked ? "rotate-fab" : ""
          }`}
          style={{ transform: trfm }} //this rotation takes care of all other rotations.
        >
          <div className="FAB" onClick={FABClick}>
            <span>Assist</span>
          </div>
          {state.fabClicked && (
            <div className="floating-container">
              <div className="floating-menu">
                <div onClick={() => sendAssistance("water")}>Ask for Water</div>
                <div onClick={() => sendAssistance("help")}>
                  Call for Assistance
                </div>
                <div onClick={() => sendAssistance("cutlery")}>
                  Call for Cutlery
                </div>
                <div onClick={() => sendAssistance("tissue")}>
                  Ask for Tissue
                </div>
                <div onClick={() => sendAssistance("cleaning")}>
                  Ask for Cleaning
                </div>
                <div onClick={() => sendAssistance("menu")}>
                  Ask for Physical Menu
                </div>
                <div onClick={() => sendAssistance("ketchup")}>
                  Ask for Ketchup
                </div>
              </div>
            </div>
          )}
        </div>
        <Link
          to="/"
          className="styled-link"
          onClick={() =>
            setState(state => ({ ...state, menuClick: false }))
          }
        >
          <div style={{ marginTop: "calc(.7rem - 3px)" }}>
            <img src={home} alt="Home" className={fillSvg("Home")} />
            <span className="icon-text">Home</span>
          </div>
        </Link>
        <Link to="/menu" className="styled-link">
          <div style={{ marginTop: "calc(.7rem - 3px)" }}>
            <img src={menu} alt="Menu" className={fillSvg("Menu")} />
            <span className="icon-text">Menu</span>
          </div>
        </Link>
        <Link
          to="/cart"
          className="styled-link"
          onClick={() =>
            setState(state => ({ ...state, menuClick: false }))
          }
        >
          <div style={{ marginTop: "calc(.7rem - 3px)" }}>
            <img src={cart} alt="Cart" className={fillSvg("Cart")} />
            <span className="icon-text">Cart</span>
          </div>
        </Link>
        <Link to="/order" className="styled-link"
        onClick={() =>
          setState(state => ({ ...state, menuClick: false }))
        }>
          <div style={{ marginTop: "calc(.7rem - 3px)" }}>
            <img src={order} alt="Table" className={fillSvg("Order")} />
            <span className="icon-text">Order</span>
          </div>
        </Link>
      </div>
    </>
  );
};

/*

*/

/* ZOMATo STYLE
      <div className="floating-container FAB">
        <span className="plus_cross">+</span>
        <div className="fab-actions">
          <ul>
            <li>Water</li>
            <li>Tissue</li>
            <li>Help</li>
            <li>..</li>
          </ul>
        </div>
      </div>
*/

const FooterNavSocket = props => (
  <SocketContext.Consumer>
    {socket => <FooterNav {...props} socket={socket} />}
  </SocketContext.Consumer>
);

export default FooterNavSocket;
