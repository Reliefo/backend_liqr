import React from "react";
import { StoreContext } from "Store";
import * as TYPES from "Store/actionTypes.js";
import FoodItem from "components/FoodItem";

const SearchFoodItems = () => {
  const {
    dispatch,
    state: { searchValue, justMenuItems }
  } = React.useContext(StoreContext);
  
  return (
    <div className="category">
      <ul style={{ listStyleType: "none" }}>
        {justMenuItems.map((foodItem,idx) => {
          //to make it case insensitive
          const name = foodItem.name.toLowerCase();
          const mathingValue = searchValue.toLowerCase();
          const isMatch = name.indexOf(mathingValue) !== -1;
          return (
            <li key={idx} style={{ display: isMatch ? "" : "none" }}>
              <FoodItem foodItem={foodItem} />
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default SearchFoodItems;
