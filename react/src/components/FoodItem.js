import React from "react";
import PlusWithAddRemove from "components/PlusWithAddRemove";
import { Card, Accordion, Modal, Button, Form } from "react-bootstrap";
import * as TYPES from "Store/actionTypes.js";
import { StoreContext } from "Store";

const FoodItem = ({ stateData, foodItem, index, subsIndex, subs }) => {

  const {
    dispatch,
    state: {
      rawData: { food_menu = [], bar_menu = [] },
      activeData,
      cart
    }
  } = React.useContext(StoreContext);

  const [state, setState] = React.useState({
    food_item: activeData //0: Personal cart, 1: Table cart
  });

  const [show, setShow] = React.useState(false);

  const selectOption = (foodItem, item) => {
    foodItem.food_option = item;
  };
  const addItem = (item, index, subsIndex) => {
    if (item["options"] === undefined) {
      item["options"] = {};
    } 
    item["options"] = item.food_option;
    dispatch({ type: TYPES.ADD_ITEM, payload: item }); //dispatcing the whole item

    activeData.forEach((item2, index3) => {
      if (index3 === subsIndex) {
        item2.food_list.forEach((item3, idx2) => {
          if (idx2 === index) {
            item3.showPopup = false;
            item3.showCustomize = false;
            item3.showOptionsAgain = false;
          }
        });
      }
    });
    dispatch({ type: TYPES.ADD_SELECT_DATA, payload: activeData });
  };
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const setIndex = (foodItem, index, subsIndex) => {
    activeData.forEach((item, index3) => {
      if (index3 === subsIndex) {
        item.food_list.forEach((item1, idx2) => {
          if (idx2 === index) {
            item1.open = !item1.open;
          }
        });
      }
    });
    dispatch({ type: TYPES.ADD_SELECT_DATA, payload: activeData });
  };

  const closePopUp = (foodItem, index, subsIndex) => {
    activeData.forEach((item, index3) => {
      if (index3 === subsIndex) {
        item.food_list.forEach((item1, idx2) => {
          if (idx2 === index) {
            item1.showPopup = !item1.showPopup;
            item1.showCustomize = false;
          }
        });
      }
    });
    dispatch({ type: TYPES.ADD_SELECT_DATA, payload: activeData });
  };

  const showOptions = (foodItem, index, subsIndex) => {
    activeData.forEach((item, index3) => {
      if (index3 === subsIndex) {
        item.food_list.forEach((item1, idx2) => {
          if (idx2 === index) {
            item1.showOptionsAgain = true;
          }
        });
      }
    });
    dispatch({ type: TYPES.ADD_SELECT_DATA, payload: activeData });
  };
  let desc = foodItem.description.substring(0, 20) + "...";
  return (
    <Accordion defaultActiveKey="0">
      <Card className="category-card food-item">
        <Accordion.Toggle
          onClick={() => setIndex(foodItem, index, subsIndex)}
          variant="link"
          eventKey={index}
        >
          <Card.Title style={{ width: "100%" }}>
            <div>
              <p style={{ float: "left" }}>{foodItem.name}</p>
              <p style={{ float: "right" }}>&#8377; {foodItem.price}</p>
            </div>
          </Card.Title>
        </Accordion.Toggle>
        {foodItem.open && foodItem.open === true ? (
          ""
        ) : (
          <div>
            <Card.Body className="Menu-body">
              <p style={{ width: "69%", fontSize: ".9rem" }}>{desc}</p>
            </Card.Body>
          </div>
        )}
        <Accordion.Collapse eventKey={index}>
          <Card.Body className="Menu-body">
            <p style={{ width: "69%", fontSize: ".9rem" }}>
              {foodItem.description}
            </p>
            <PlusWithAddRemove item={foodItem} idx={index} subs={subsIndex} />
          </Card.Body>
        </Accordion.Collapse>
      </Card>
      {foodItem.foodOptions && foodItem.foodOptions === true ? (
        <Modal show={foodItem.showPopup} onHide={handleClose}>
          <Modal.Header>
            <Modal.Title className="options-title">
              {foodItem.name} <br />{" "}
              <div className="options-modal">{foodItem.description}</div>
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {cart.length
              ? cart.map(item => {
                  if (foodItem._id.$oid === item._id.$oid) {
                    return (
                      <div>
                        <div>
                          <p
                            style={{
                              width: "69%",
                              fontSize: ".9rem",
                              float: "left"
                            }}
                          >
                            Rs {item.options.option_price} <br />
                            Option:
                            {item.options.option_name} <br />
                          </p>
                          <PlusWithAddRemove
                            item={foodItem}
                            idx={index}
                            subs={subsIndex}
                          />
                          <br />
                        </div>
                      </div>
                    );
                  }
                })
              : ''}
            {foodItem.options ? '' : Object.entries(foodItem.food_options).map((item, index) => {
                  return Object.values(item[1]).map((item1, idx) => {
                    return (
                      <div key={idx}>
                        <Form.Check
                          onClick={() => selectOption(foodItem, item1)}
                          type="radio"
                          label={item1.option_name}
                          name="test"
                        />
                      </div>
                    );
                  });
                }) }
            {foodItem.showCustomize ? (
              <div
                className="modal-customization"
                onClick={() => showOptions(foodItem, index, subsIndex)}
              >
                Add More Customization
              </div>
            ) : (
              ""
            )}
            {foodItem.showOptionsAgain
              ? Object.entries(foodItem.food_options).map((item, index) => {
                  return Object.values(item[1]).map((item1, idx) => {
                    return (
                      <div key={idx}>
                        <Form.Check
                          onClick={() => selectOption(foodItem, item1)}
                          type="radio"
                          label={item1.option_name}
                          name="test"
                        />
                      </div>
                    );
                  });
                })
              : ""}
            {/* Customizable Options: <br />
            {Object.entries(foodItem.food_options).map((item, index) => {
              return Object.values(item[1]).map((item1, idx) => {
                return (
                  <div key={idx}>
                    <Form.Check
                      onClick={() => selectOption(foodItem, item1)}
                      type="radio"
                      label={item1.option_name}
                      name="test"
                    />
                  </div>
                );
              });
            })} */}
          </Modal.Body>

          <Modal.Footer>
            <Button
              variant="secondary"
              onClick={() => closePopUp(foodItem, index, subsIndex)}
            >
              Close
            </Button>
            <Button
              variant="primary"
              onClick={() => addItem(foodItem, index, subsIndex)}
            >
              Add
            </Button>
          </Modal.Footer>
        </Modal>
      ) : (
        ""
      )}
    </Accordion>
  );
};

export default FoodItem;
