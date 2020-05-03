import React from "react";
import reducer from "./reducer.js";
import axios from "axios";
import * as TYPES from "./actionTypes";
import { v4 as uuidv4 } from "uuid";
import tempData from "json_with_class.json";
import io from "socket.io-client";

const initialState = {
  activeNav: "",
  justMenuItems: [], //for search
  searchClicked: false,
  searchValue: "",
  cart: [],
  tableId: "",
  placeOrderById: "",
  tableOrders: [],
  justBarItems: [],
  homeItems: [],
  orderSuccess: [],
  orderStatus: [],
  activeData: {},
  rawData: {}
};

const localState = JSON.parse(sessionStorage.getItem("relief"));

const StoreContext = React.createContext(null);
const Store = props => {
  const [state, dispatch] = React.useReducer(
    reducer,
    localState || initialState
  );

  let parm = window.location.href;
  parm = parm.split("=");

  React.useEffect(() => {
    sessionStorage.setItem("relief", JSON.stringify(state));
  }, [state]);

  const getData = async () => {
    try {
      const resp = await axios.get(
        "http://ec2-13-232-202-63.ap-south-1.compute.amazonaws.com:5050/rest"
      );
      return resp.data;
    } catch (err) {
      return { success: false };
    }
  };
  React.useEffect(() => {
    console.log("store mounted");
   

    getData().then(resp => {
      if (!resp.success) {
        dispatch({ type: TYPES.ADD_DATA, payload: resp });
        dispatch({ type: TYPES.ADD_SELECT_DATA, payload: resp.food_menu });
        //segregating the food items and storign for search
        // console.log({ resp });

        // resp.tables.forEach(item => {
        //   if (item.users.length > 0) {
        //     dispatch({
        //       type: TYPES.SET_TABLE_ID,
        //       payload: item
        //     });

        //     dispatch({
        //       type: TYPES.SET_PLACEORDER_ID,
        //       payload: item
        //     });
        //   }
        // });

        let justBarItems = [];
        let justFoodItems = [];
        const barMenu = resp.bar_menu;
        for (let i = 0; i < barMenu.length; ++i) {
          const Sub = resp.food_menu[i].name;
          for (let j = 0; j < resp.bar_menu[i].food_list.length; ++j) {
            justFoodItems.push(resp.bar_menu[i].food_list[j]);
            // const FoodList = Sub[j].foodlist;
            // for (let k = 0; k < FoodList.length; ++k) {
            //   justFoodItems.push(FoodList[k]);
            // }
          }
        }

        const Menu = resp.food_menu;
        for (let i = 0; i < Menu.length; ++i) {
          const Sub = resp.food_menu[i].name;
          for (let j = 0; j < resp.food_menu[i].food_list.length; ++j) {
            justFoodItems.push(resp.food_menu[i].food_list[j]);
            // const FoodList = Sub[j].foodlist;
            // for (let k = 0; k < FoodList.length; ++k) {
            //   justFoodItems.push(FoodList[k]);
            // }
          }
        }
        dispatch({
          type: TYPES.ADD_COLLECTIVE_FOODITEMS,
          payload: justFoodItems
        });
      }
    });
  }, []);

  const value = {
    state,
    dispatch
  };
  return (
    <StoreContext.Provider value={value}>
      {props.children}
    </StoreContext.Provider>
  );
};
export { StoreContext, Store };
