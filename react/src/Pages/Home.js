import React from "react";
import { Card, CardDeck, Image } from "react-bootstrap";
import PlusWithAddRemove from "components/PlusWithAddRemove";
import dummyPic from "assets/dummypic.jpeg";
import HomeItem from "components/HomeItem";
import { Toast } from "react-bootstrap";
import vodkaPic from "assets/vodka.jpg";
import SearchFoodItems from "components/SearchFoodItems.js";
import SocketContext from "../socket-context";
import Slider from "react-slick";
import { StoreContext } from "Store";
import * as TYPES from "Store/actionTypes.js";

const Home = props => {
  const {
    dispatch,
    state: {
      homeItems,
      rawData: { food_menu = [] },
      searchClicked
    }
  } = React.useContext(StoreContext);

  let settings = {
    dots: false,
    infinite: true,
    speed: 500,
    slidesToShow: 3,
    slidesToScroll: 3,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 3,
          infinite: true,
          dots: false
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 2,
          initialSlide: 2
        }
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1
        }
      }
    ]
  };

  const [state, setState] = React.useState({
    active: false,
    subMenu: [] //0: Personal cart, 1: Table cart
  });

  React.useEffect(() => {
    console.log("home screen");
    dispatch({ type: TYPES.SET_GENERAL_DATA, payload: { searchValue: '' } });
    dispatch({
      type: TYPES.SET_GENERAL_DATA,
      payload: { searchClicked: false }
    });
    dispatch({ type: TYPES.SET_NAV, payload: "Home" });
    props.socket.off("order_updates").on("order_updates", msg => {
      dispatch({ type: TYPES.UPDATE_ORDER_STATUS, payload: JSON.parse(msg) });
    });
    console.log(props.socket);

    props.socket.emit("fetch_rest_customer", "BNGHSR0001");
    props.socket.off("home_screen_lists").on("home_screen_lists", msg => {
      dispatch({ type: TYPES.UPDATE_HOME_ITEMS, payload: JSON.parse(msg) });
    });
  }, []);

  return (
    <>
      {searchClicked === true ? (
        <SearchFoodItems />
      ) : (
        <div className="category">
          {Object.entries(homeItems).map((data, idx) => {
            if (idx !== 0) {
              return (
                <Card
                  className="category-card main-home-card"
                  key={`category-cards-${idx}`}
                >
                  <Card.Title className="home-title">{data[0]}</Card.Title>
                  <Slider {...settings}>
                    {Object.values(data[1]).map((item, index) => {
                      if (typeof item === "object") {
                        return Object.entries(data[1]).map((subMenu, sbx) => {
                          return (
                            <Card
                              onClick={() =>
                                props.history.push("/submenu", {
                                  data: subMenu,
                                  sbx: sbx,
                                  foodMenu: food_menu
                                })
                              }
                              className="category card home-item"
                              key={`category-cards-${sbx}`}
                            >
                              <Card.Title className="category-body home-title-font">
                                {subMenu[0]}
                              </Card.Title>
                            </Card>
                          );
                        });
                      }
                      return Object.values(food_menu).map((food, idx) => {
                        return Object.values(food.food_list).map((list, ix) => {
                          let desc = list.description.substring(0, 40) + "...";
                          if (list._id.$oid === item) {
                            return (
                              <Card
                                className="category card home-item"
                                key={`category-cards-${ix}`}
                              >
                                <Card.Title className="category-body home-title-font">
                                  {list.name.toLowerCase()}
                                </Card.Title>
                                <Card.Body>
                                  <p className="desc-home-body">{desc}</p>
                                  <PlusWithAddRemove item={list} idx={ix} subs={idx} />
                                </Card.Body>
                              </Card>
                            );
                          }
                        });
                      });
                    })}
                  </Slider>
                </Card>
              );
            }
          })}
        </div>
      )}
    </>
  );
};

const homeWithSocket = props => (
  <SocketContext.Consumer>
    {socket => <Home {...props} socket={socket} />}
  </SocketContext.Consumer>
);

export default homeWithSocket;
