import React from "react";
import { StoreContext } from "Store";
import * as TYPES from "Store/actionTypes.js";

//used in menu, menu has lots of items
const UpdateFoodItem = ({ item }) => {
  const {
    dispatch,
    state: { cart }
  } = React.useContext(StoreContext);

  const [state, setState] = React.useState({
    showAddRemove: false,
    count: null //if 0,delt effect fires up //maintaining internal state, so that we don't need to pull individual card state from the store
  });


//   React.useEffect(() => {
//     const idx = cart.findIndex(itm => itm._id.$oid === item._id.$oid);
//     if (cart.length > 0 && idx !== -1) {
//       setState(state => ({
//         ...state,
//         count: cart[idx].count,
//         showAddRemove: true
//       }));
//     }
//   }, []);

  //if count is 0, then we show plus button.
  
 

};

export default UpdateFoodItem;
