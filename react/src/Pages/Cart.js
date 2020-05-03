/* eslint-disable no-unused-expressions */
import React from "react";
import { Link } from "react-router-dom";
import { Card, Row, Col } from "react-bootstrap";
import AddRemoveItem from "components/AddRemoveItem.js";
import { StoreContext } from "Store";
import SocketContext from "../socket-context";
import * as TYPES from "Store/actionTypes.js";
import SearchFoodItems from "components/SearchFoodItems.js";
import { ReactComponent as FoodTraySVG } from "assets/food-tray.svg";
import { ReactComponent as TableSVG } from "assets/table.svg";
import { ReactComponent as EmptyCartSadIMG } from "assets/empty-card-sad.svg";
import CloseSVG from "components/CloseSVG.js";
import _ from "lodash";
import { Table as RBTable } from "react-bootstrap";
import Bill from "components/Bill.js";
import { ReactComponent as TableFilledIMG } from "assets/Table-Filled.svg";
import { ReactComponent as PersonalSVG } from "assets/personal.svg";

const Cart = props => {
  const {
    dispatch,
    state: { cart, tableId, tableOrders, placeOrderById, searchClicked }
  } = React.useContext(StoreContext);

  const [state, setState] = React.useState({
    activeCart: 0 //0: Personal cart, 1: Table cart
  });

  React.useEffect(() => {
    console.log("Cart screen");
    dispatch({ type: TYPES.SET_GENERAL_DATA, payload: { searchValue: '' } });
    dispatch({
      type: TYPES.SET_GENERAL_DATA,
      payload: { searchClicked: false }
    });
    //handling refresh issue
    dispatch({ type: TYPES.SET_NAV, payload: "Cart" });
  }, []);

  const DeleteItemHndlr = item => {
    dispatch({ type: TYPES.DEL_ITEM, payload: item });
  };

  const pushToCart = () => {
    setState(state => ({ ...state, activeCart: 1 - state.activeCart }));
  };

  const setOrderTable = () => {
    const body = { table_id: localStorage.getItem('table_id') };
    props.socket.emit("place_table_order", JSON.stringify(body));
    props.socket.off("new_orders").on("new_orders", msg => {
      dispatch({ type: TYPES.UPDATE_SUCCESS_ORDER, payload: JSON.parse(msg) });
    });
  };

  const setCartPlaceOrder = () => {
    const cartClone = _.cloneDeep(cart);

    cartClone.forEach(item => {
      item.food_id = item._id.$oid;
      delete item.open;
      delete item.food_options;
      item.food_options = {};
      item.food_options.options = [];
      delete item.restaurant;
      delete item.showCustomize;
      delete item.showPopup;
      delete item.showOptionsAgain;
      item.food_options.options.push(item.options)
      delete item.foodOptions;
      delete item.options;
      delete item.food_option;
      delete item.tags;
      delete item._id;
    });

    const body = {
      table: tableId,
      orders: [{ placed_by: localStorage.getItem('user_id'), food_list: cartClone }]
    };

    props.socket.emit("place_personal_order", JSON.stringify(body));
    props.socket.off("new_orders").on("new_orders", msg => {
      dispatch({ type: TYPES.UPDATE_SUCCESS_ORDER, payload: JSON.parse(msg) });
    });
  };

  const setCart = () => {
    const cartClone = _.cloneDeep(cart);
    cartClone.forEach(item => {
      item.food_id = item._id.$oid;
      delete item.open;
      delete item.showPopup;
      delete item.food_options
      delete item.showCustomize;
      delete item.restaurant;
      item.food_options = {};
      item.food_options.options = [];
      item.food_options.options.push(item.options)
      delete item.showOptionsAgain;
      delete item.options;
      delete item.foodOptions;
      delete item.food_option;
      delete item.tags;
      delete item._id;
    });

    const body = {
      table: tableId,
      orders: [{ placed_by: localStorage.getItem('user_id'), food_list: cartClone }]
    };
    props.socket.emit("push_to_table_cart", JSON.stringify(body));
    props.socket.off("table_cart_orders").on("table_cart_orders", msg => {
      dispatch({ type: TYPES.UPDATE_TABLE_ORDER, payload: JSON.parse(msg) });
    });
  };

  // setState(state => ({ ...state, activeCart: 1 - state.activeCart }));

  const renderPersonalCart = () => (
    <>
      {cart.map((item, idx) => (
        <Card className="cart-card cart-styling" key={`cart-card-${idx}`}>
          <Card.Body className="body">
            <p className="name">{item.name}</p>
            <AddRemoveItem
              className="trial"
              count={item.quantity}
              id={item}
              allData={item}
            />
            <p style={{ margin: 0, width: "15%" }}>
              &#8377; {item.options ? parseInt(item.options.option_price * item.quantity) : item.price * item.quantity}
            </p>
            <div
              style={{ padding: ".5rem" }}
              onClick={DeleteItemHndlr.bind(this, item)}
            >
              <CloseSVG />
            </div>
          </Card.Body>
        </Card>
      ))}
    </>
  );
  const renderTableCart = () => (
    <>
      {Object.entries(tableOrders).map((item2, idx) => {
        if (item2[0] === "orders") {
          return item2[1].map((order_list, index) => {
            return (
              <React.Fragment key={`table-${index}`}>
                <RBTable striped bordered hover>
                  <thead className="table-thead">
                    <tr>
                      <th>Name</th>
                      <th>Qty</th>
                      <th>Price</th>
                    </tr>
                  </thead>
                  {order_list.food_list.map((food, ix) => {
                    return (
                      <tbody>
                        <tr>
                          <td>{food.name}</td>
                          <td>{food.quantity}</td>
                          <td>{food.price}</td>
                        </tr>
                      </tbody>
                    );
                  })}
                </RBTable>
              </React.Fragment>
            );
          });
        }
      })}
    </>
  );
  //TODO: useEffect for this
  const orderTotal =
    cart.length !== 0
      ? cart.reduce((total, item) => total + (item.options ? parseInt(item.options.option_price) * item.quantity: item.price * item.quantity), 0)
      : "";

 
 

  let sum = 0;
  tableOrders.length !== 0
    ? Object.entries(tableOrders).forEach(item => {
        if (item[0] === "orders") {
          item[1].forEach(item2 => {
            item2.food_list.forEach(item3 => {
              sum += parseInt(item3.price * item3.quantity);
            });
          });
        }
      })
    : "";

  const isEmpty = () => {
    if (state.activeCart === 0 && cart.length === 0) return true;
    if (state.activeCart === 1) return false; //TODO: figure this out
  };
  return (
    <>
      {searchClicked === true ? (
        <SearchFoodItems />
      ) : (
        <div>
          <ul className="menu-btn" style={{ justifyContent: "space-evenly" }}>
            <li onClick={pushToCart}>
              <div
                className={
                  state.activeCart === 0 ? "cart-menu active" : "cart-menu"
                }
              >
                <PersonalSVG height="19px" />
                &nbsp;&nbsp;Personal
              </div>
            </li>
            <li onClick={pushToCart}>
              <div
                className={
                  state.activeCart === 1 ? "cart-menu active" : "cart-menu"
                }
              >
                <TableSVG height="19px" />
                &nbsp;&nbsp;Table
              </div>
            </li>
          </ul>
          <div className="cart-wrapper">
            {isEmpty() && (
              <div className="empty-cart">
                <EmptyCartSadIMG />
                <p style={{ margin: 0 }}>Who likes rumbling tummy ?</p>
                <p>Neither me.</p>
              </div>
            )}
            {cart.length !== 0 &&
              state.activeCart === 0 &&
              renderPersonalCart()}
            {state.activeCart === 1 && renderTableCart()}
            {state.activeCart === 0 && cart.length !== 0 && (
              <>
                <Bill orderTotal={orderTotal} />
                {state.activeCart === 0 && (
                  <Row>
                    <Col style={{ marginTop: "1rem" }}>
                      <div className="bill-btn" onClick={setCartPlaceOrder}>
                        <FoodTraySVG height="25px" width="25px" />
                        <p>Place Order</p>
                      </div>
                    </Col>
                    <Col style={{ marginTop: "1rem" }}>
                      <div className="bill-btn" onClick={setCart}>
                        <TableSVG height="25px" width="25px" />
                        <p>Push To Table</p>
                      </div>
                    </Col>
                  </Row>
                )}
              </>
            )}
            {state.activeCart === 1 && (
              <>
                <Bill orderTotal={sum} />
                <div onClick={setOrderTable} className="bill-btn mt-3">
                  <div className="d-flex">
                    <FoodTraySVG height="25px" width="25px" />
                    <p className="ml-3">Confirm Order</p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
};

const cartWithSocket = props => (
  <SocketContext.Consumer>
    {socket => <Cart {...props} socket={socket} />}
  </SocketContext.Consumer>
);

export default cartWithSocket;
