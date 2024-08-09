function login() {
    // Get the username and password from the form
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
  
    // Send a request to the server to authenticate the user
    // Assume the server returns a success message if the login is successful
    if (authenticateUser(username, password)) {
      // Redirect to the homepage
      window.location.href = "homepage.html";
    } else {
      // Display an error message
      alert("Incorrect username or password");
    }
  }
  