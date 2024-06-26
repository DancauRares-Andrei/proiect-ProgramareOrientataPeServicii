// LogoutPage.js
import React, { useEffect } from 'react';

const LogoutPage = (props) => {
  if(props.token === undefined){
    props.resetProps();
        window.location.href = '/login';
  }
  useEffect(() => {//componentDidMount 
    const logoutUser = async () => {
      if (props.token) {
        try {
          const response = await fetch('http://localhost:8002/logout', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${props.token}`,
            },
          });
          if(response.status===401 || response.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
          if (response.status===204) {
             props.resetProps();
            window.location.href = '/';
          } else {
            console.error('Logout failed:', response.statusText);
          }
        } catch (error) {
          console.error('Error during logout:', error);
        }
      } else {
        props.resetProps();
        window.location.href = '/';
      }
    };

    logoutUser();
  }, [props]);

  return (//render
    <div className="container mt-5">
    <h2>Pagina de logout</h2>
    <div>
      <p>Se efectuează logout...</p>
    </div>
  </div>
  );
};

export default LogoutPage;

