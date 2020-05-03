import React from "react";
import { Card } from "react-bootstrap";

const Bill = ({orderTotal }) => (
  <Card className="cart-bill cart-styling">
    <Card.Title className="pl-3 pt-3 brand-clr" style={{ fontWeight: 600 }}>
      Bill
    </Card.Title>
    <Card.Body>
      <div className="d-flex justify-content-between">
        <p style={{ fontWeight: 500 }}>Order total</p>
        <p>&#8377; {orderTotal}</p>
      </div>
      <div className="d-flex justify-content-between">
        <p style={{ fontWeight: 500 }}>Taxes & Charges</p>
        <p>&#8377; 50</p>
      </div>
      <div className="d-flex justify-content-between">
        <p style={{ fontWeight: 500 }}>Pay</p>
        <p>&#8377; {orderTotal + 50}</p>
      </div>
    </Card.Body>
  </Card>
);
export default Bill;