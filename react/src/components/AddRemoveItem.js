import React from "react";
import { ReactComponent as MinuSVG } from "assets/minus.svg";
import { ReactComponent as MyPlusSVG } from "assets/myPlus.svg";
import { StoreContext } from "Store";
import * as TYPES from "Store/actionTypes.js";

//decHndlr and incHndlr are for parent.(we are using it in case of plusWithAddRemove COmponent)
const AddRemoveItem = ({
  allData,
  id,
  count,
  decHndlr,
  incHndlr,
  className,
  svgClassName,
  wrapperStyles = {}
}) => {
  const { dispatch } = React.useContext(StoreContext);

  const increase = () => {
    dispatch({
      type: TYPES.INC_ITEM,
      payload: id
    });
    if (incHndlr) {
      incHndlr();
    }
  };
  const decrease = () => {
    if (count === 0) return;
    dispatch({
      type: TYPES.DEC_ITEM,
      payload: id
    });
    if (decHndlr) {
      decHndlr();
    }
  };
  return (
    <div
      className={`d-flex ${className}`}
      style={{ fontWeight: 600, ...wrapperStyles }}
    >
      <div className="icon">
        <MinuSVG onClick={decrease} className={svgClassName} />
      </div>
      {count}
      <div className="icon">
        <MyPlusSVG onClick={increase} className={svgClassName} />
      </div>
    </div>
  );
};

export default AddRemoveItem;
