import React from "react";
import { StoreContext } from "Store";
import { Card, Accordion, Button } from "react-bootstrap";
import SocketContext from "../socket-context";
import SearchFoodItems from "components/SearchFoodItems.js";

import * as TYPES from "Store/actionTypes.js";

const Table = props => {
  const {
    dispatch,
    state: {
      rawData: { food_menu = [] },
      orderSuccess,
      searchClicked
    }
  } = React.useContext(StoreContext);

  React.useEffect(() => {
    dispatch({ type: TYPES.SET_GENERAL_DATA, payload: { searchValue: '' } });
    console.log("Table screen");
    //handling refresh issue
    dispatch({
      type: TYPES.SET_GENERAL_DATA,
      payload: { searchClicked: false }
    });
    dispatch({ type: TYPES.SET_NAV, payload: "Order" });
  }, []);

  return (
    <>
      {searchClicked === true ? (
        <SearchFoodItems />
      ) : (
        <div className="order-status-styling">
          {food_menu.map((menuItem, index) => {
            return menuItem.food_list.map(foodItem => {
              return orderSuccess.map((item, idx) => {
                return item.payload.orders.map(item2 => {
                  return item2.food_list.map(item3 => {
                    if (item3.food_id === foodItem._id.$oid) {
                      return (
                        <Card
                          key={idx}
                          className="cart-card cart-styling margin-styling"
                        >
                          <Card.Body className="body">
                            {foodItem.name} - {item3.status}
                          </Card.Body>
                        </Card>
                      );
                    }
                  });
                });
              });
            });
          })}
        </div>
      )}
    </>
  );
};

const tableWthSocket = props => (
  <SocketContext.Consumer>
    {socket => <Table {...props} socket={socket} />}
  </SocketContext.Consumer>
);

export default tableWthSocket;
