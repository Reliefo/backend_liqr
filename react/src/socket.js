import io from "socket.io-client";



  const socket = io(
    "http://ec2-13-232-202-63.ap-south-1.compute.amazonaws.com:5050/reliefo",
    {
      transportOptions: {
        polling: {
          extraHeaders: {
            Authorization:
              "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODc3MjE4OTEsIm5iZiI6MTU4NzcyMTg5MSwianRpIjoiOTdjZWZmZmQtOTI2YS00MGNkLWJkNmUtZjkwOThkYzA3ZWY4IiwiZXhwIjoxNTg3NzM2ODkxLCJpZGVudGl0eSI6IktJRDAwMSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.5nm33ZbJcRQRJI7_F35AdbZhumnEzKXAILG2BiNEX5k"
          }
        }
      }
    }
  );
<<<<<<< HEAD

export default socket;
=======
export default socket;
>>>>>>> 0fa80e8752b998ff1578d78029dd18ee9b1c1e4f
