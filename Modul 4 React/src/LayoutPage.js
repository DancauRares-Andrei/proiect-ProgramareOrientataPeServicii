import React from 'react';
import { Outlet} from "react-router-dom";
const LayoutPage = () => {
  return(
  <div className="container mt-4">
    <h1 className="mb-4">REST Medicine</h1>
    <Outlet />
  </div>
  );
};

export default LayoutPage;
