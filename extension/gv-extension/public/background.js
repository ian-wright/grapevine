

// on startup event, attempt to validate the GV auth-token
// maintain window-level state that flags whether or not auth-token is valid
// if valid, request a set of friends from GV '/list-confirmed-friends' endpoint; hold that as window-level state too
chrome.runtime.onStartup.addListener(function() {
	GVvalid = true;
	GVoptions = [
		{
	        first_name: 'Mike',
	        last_name: 'Cancilla',
	        email: 'mc@gmail.com'
	    },
	    {
	        first_name: 'Flora',
	        last_name: 'Devlin',
	        email: 'fd@gmail.com'
	    },
	    {
	        first_name: 'Piers',
	        last_name: 'Bonifant',
	        email: 'pb@gmail.com'
	    }
	];
	// test for jQuery
	if (axios) {
		console.log("we have axios");
	} else {
		console.log("no bueno on the axios");
	};
});

chrome.runtime.onInstalled.addListener(function() {
	GVvalid = true;
	GVoptions = [
		{
	        first_name: 'Mike',
	        last_name: 'Cancilla',
	        email: 'mc@gmail.com'
	    },
	    {
	        first_name: 'Flora',
	        last_name: 'Devlin',
	        email: 'fd@gmail.com'
	    },
	    {
	        first_name: 'Piers',
	        last_name: 'Bonifant',
	        email: 'pb@gmail.com'
	    }
	];
	// test for jQuery
	if (axios) {
		console.log("we have axios");
	} else {
		console.log("no bueno on the axios");
	};
});

function getGVvalid() {
	return GVvalid;
}


// background message listener
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {

    if (request.action == "share") {

    	share(request.url, request.receiverEmails, function() {
    		// do stuff here
    		// get activeTab URL
    		sendResponse({msg: "handled share request"})
    	});

    } else if (request.action == "login") {
    	login(request.email, request,password, function() {
			// do stuff here
    		sendResponse({msg: "handled login request"});
    	});
 

    } else if (request.action == "logout") {
    	logout(function() {
			// do stuff here
    		sendResponse({msg: "handled logout request"});
    	});
    }
});

const getActiveURL = () => {
	let activeURL;
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		activeURL = tabs[0].url;
	}
	return activeURL;
}



// listen for 'share' message sent from popup
// share the URL via GV '/send-share' endpoint
const share = (url, receiverEmails, cb) => {
	console.log("sharing!");
	cb();
}


// listen for 'login' message sent from popup
// login and store a valid token via GV '/login' endpoint
// send a success/failure message back to popup; if success, send the friend options to popup too
const login = (email, password, cb) => {
	console.log("logging in!");
	cb();
}


// listen for 'logout' message sent from popup
// logout and remove token via GV '/logout' endpoint
// send a success/failure message back to popup
const logout = (cb) => {
	console.log("logging out!");
	cb();
}








// validateToken(token) {
//         if (token == null) {
//             // called before component is mounted
//             this.state = {isTokenValid: false};
//             console.log("isTokenValid:", this.state.isTokenValid);
//         } else {
//             const baseURL = this.props.APIbaseURL;
//             axios({
//                 method: 'get',
//                 url: baseURL + '/validate-token',
//                 headers: {'auth-token': token}
//             }).then((response) => {
//                 // response status 200 - OK
//                 this.setState({
//                     isTokenValid: true,
//                     user: {
//                         firstName: response.data.first_name,
//                         lastName: response.data.last_name,
//                         email: response.data.email
//                     }
//                 });
//                 console.log("isTokenValid:", this.state.isTokenValid);
//             }).catch((error) => {
//                 if (error.response) {
//                     // server side error
//                     console.log("couldn't validate token with server");
//                     this.setState({isTokenValid: false}); 
//                     console.log("isTokenValid:", this.state.isTokenValid);
//                 } else if (error.request) {
//                     // client side error
//                     console.log("problem sending token validation request on client side");
//                     console.log(error.request);
//                 } else {
//                     console.log("error validating token");
//                     console.log(error.message);
//                 }
//             });
//         }
//     }

//     login(email, password) {
//         console.log("logging in...")
//         const baseURL = this.props.APIbaseURL;
//         console.log("baseURL:", baseURL);
//         axios({
//             method: 'post',
//             url: baseURL + '/login',
//             data: {
//                 email: email,
//                 password: password
//             }
//         }).then((response) => {
//             // response status 200 - OK
//             console.log("response.data", response.data);
//             // save the token
//             const token = response.data.response.user.authentication_token;
//             const user = response.data.response.user;
//             localStorage.setItem('authToken', token);
//             this.setState({
//                 isTokenValid: true,
//                 authToken: localStorage.getItem('authToken'),
//                 user: {
//                     firstName: user.first_name,
//                     lastName: user.last_name,
//                     email: user.email
//                 }
//             });
//         }).catch((error) => {
//             if (error.response) {
//                 console.log(error.response.data);
//             } else if (error.request) {
//                 console.log(error.request);
//             } else {
//                 console.log(error.message);
//             }
//         });  
//     }

//     // add an API call to logout
//     logout() {
//         console.log("killing token; logging out.")
//         localStorage.removeItem('authToken');
//         this.setState({
//             authToken: localStorage.getItem('authToken'),
//             isTokenValid: null
//         });
//     }