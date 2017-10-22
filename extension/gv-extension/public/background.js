// on startup event, attempt to validate the GV auth-token
// maintain window-level state that flags whether or not auth-token is valid
// if valid, request a set of friends from GV '/list-confirmed-friends' endpoint; hold that as window-level state too
GVstate = {
	url: 'http://localhost:5000',
	token: null,
	valid: null,
	friends: null,
	user: null
}

chrome.runtime.onStartup.addListener(function() {
	// validate the token, only fetch friends if token is valid
	// otherwise, require a fresh login
	validateToken(updateState, killState);
});

chrome.runtime.onInstalled.addListener(function() {
	validateToken(updateState, killState);
});

const validateToken = (successCallback, failureCallback) => {
	GVstate.token = localStorage.getItem('authToken');
	if (GVstate.token == null) {
        console.log("no token available...")
		GVvalid = false;
	} else {
        console.log("validating token...")
		axios({
            method: 'get',
            url: GVstate.url + '/validate-token',
            headers: {'auth-token': GVstate.token}
        }).then((response) => {
            // response status 200 - OK
            successCallback(response.data, function() {console.log("updated background state after token validation.")});
        }).catch((error) => {
            if (error.response) {
            	failureCallback(error);
            } else if (error.request) {
                console.log(error.request);
            } else {
                console.log(error.message);
            };
        });
	}
}

// set background state (with exception of token) after validation or login (optional callback)
const updateState = (userData, cb) => {
    console.log("updating background state...");
	GVstate.valid = true;
    GVstate.user = {
        firstName: userData.first_name,
        lastName: userData.last_name,
        email: userData.email
    };
    if (cb) {
        fetchFriends(cb); 
    } else {
        fetchFriends();
    }
}

// fetch friends with an optional callback
const fetchFriends = (cb) => {
    console.log("fetching friends...");
    // fake API call to populate the state friends for testing
    GVstate.friends = [
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
    if (cb) {
        cb()
    };

	// axios({
 //        method: 'get',
 //        url: GVstate.url + '/list-confirmed-friends',
 //        headers: {'auth-token': GVstate.token}
 //    }).then((response) => {
 //        // response status 200 - OK
 //        GVstate.friends = response.data.confirmed_friends;
 //    }).catch((error) => {
 //    	console.log("couldn't fetch friend payload list");
 //        if (error.response) {
 //        	console.log(error.response);
 //        } else if (error.request) {
 //            console.log(error.request);
 //        } else {
 //            console.log(error.message);
 //        }
 //    });
}

// callback function for token validation failure
const killState = (error) => {
    console.log("kiling state...");
    if (error) {
        console.log(error.response);  
    }
    GVstate.valid = false;
    GVstate.token = null;
    GVstate.friends = null;
    GVstate.user = null;
}

// background message listener
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {

    if (request.action == "share") {
        // get activeTab URL
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            const activeURL = tabs[0].url;
            share(activeURL, request.selection, function() {
                sendResponse({msg: "handled share request"})
            });
        });
        // indicate that the response to popup will be sent async
        return true;

    } else if (request.action == "login") {
        login(request.email, request.password, function() {
            sendResponse({msg: "handled login request"})
        });
        return true;

    } else if (request.action == "logout") {
    	logout(function() {
    		sendResponse({msg: "handled logout request"});
    	});
        return true;
    }
});

// listen for 'share' message sent from popup
// share the URL via GV '/send-share' endpoint
const share = (url, receiverEmails, cb) => {
    receiverEmails.forEach(function(email) {
        console.log("sharing " + url + " to " + email);
    });
	cb();
}

// login and store a valid token via GV '/login' endpoint
// send a success/failure message back to popup; if success, send the friends to popup too
const login = (email, password, cb) => {
	console.log("logging in...");
    axios({
        method: 'post',
        url: GVstate.url + '/login',
        data: {
            email: email,
            password: password
        }
    }).then((response) => {
        // response status 200 - OK
        console.log("login response:", response.data);
        // save the token
        const userData = response.data.response.user;
        const token = userData.authentication_token;
        localStorage.setItem('authToken', token);
        GVstate.token = token;
        updateState(userData, cb)
    }).catch((error) => {
        if (error.response) {
            console.log(error.response.data);
        } else if (error.request) {
            console.log(error.request);
        } else {
            console.log(error.message);
        }
    });
}


// listen for 'logout' message sent from popup
// logout and remove token via GV '/logout' endpoint
// send a success/failure message back to popup
const logout = (cb) => {
	console.log("logging out!");
	cb();
}






//     // add an API call to logout
//     logout() {
//         console.log("killing token; logging out.")
//         localStorage.removeItem('authToken');
//         this.setState({
//             authToken: localStorage.getItem('authToken'),
//             isTokenValid: null
//         });
//     }