import React from "react";

/*CloseSVG when imported as ReactComponent , doesn't passes fill prop to svg, hence using the code of that svg itself*/
const CloseSVG = ({ onDeleteHandler, value, id }) => {
  const closeSVGPath = `M0.486294 0.486293C1.13469 -0.162099 2.18594 -0.162097
  2.83433 0.486294L8.00015 5.65212L13.166 0.486294C13.8144 -0.162097 14.8656
  -0.162099 15.514 0.486293C16.1624 1.13468 16.1624 2.18593 15.514 2.83433L10.3482
  8.00015L15.5137 13.1657C16.1621 13.8141 16.1621 14.8653 15.5137 15.5137C14.8653 16.1621
  13.8141 16.1621 13.1657 15.5137L8.00015 10.3482L2.83464 15.5137C2.18624 16.1621 1.13499
  16.1621 0.4866 15.5137C-0.161791 14.8653 -0.161792 13.8141 0.4866 13.1657L5.65212 8.00015L0.486293
  2.83433C-0.162098 2.18593 -0.162098 1.13468 0.486294 0.486293Z`;

  return (
    <svg
      value={value}
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      //   onClick={onDeleteHandler}
      id={id}
      className="icon-delete"
    >
      <path
        value={value}
        fillRule="evenodd"
        clipRule="evenodd"
        d={closeSVGPath} //
      />
    </svg>
  );
};

export default CloseSVG;
