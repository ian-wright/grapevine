// module-level settings object
(function() {
    var c;
    var n;
    var Friends = {

        nodes: {
            addFriendButton: $("#add-friend-button"),
            confirmFriendRequestButton: $("#confirm-friend-request-button"),
            deleteFriendRequestButton: $("#delete-friend-request-button"),
            addFriendEmail: $("#add-friend-email"),
            ajaxAlerts: $("#ajax-alerts")
        },

        context: {
            current_user: null
        },

        init: function (current_user) {
            // give easy access to settings for everything in module
            n = this.nodes;
            c = this.context;
            this.bindUIActions();
            this.bindUserData(current_user);

            console.log(`current user: ${c.current_user.first_name} ${c.current_user.last_name}`);
        },

        bindUserData: function (current_user) {
            c.current_user = current_user;
        },

        bindUIActions: function () {
            n.addFriendButton.on("click", function () {
                Friends.addFriend(n.addFriendEmail.val());
            });
            n.confirmFriendRequestButton.on("click", function () {
                Friends.confirmFriendRequest(n.addFriendEmail.val());
            });
        },

        render: function () {
            // build the friend request rows here (binded to friend request objects)
        },

        addFriend: function (target_email) {
            console.log("attempting to add friend:", target_email);
            var data = {target_email: target_email};
            $.ajax({
                type : "POST",
                url : "/add-friend",
                data: JSON.stringify(data),
                contentType: 'application/json;charset=UTF-8',
                success: function(resp) {
                    n.ajaxAlerts.text(resp);
                }
            });
        },

        confirmFriendRequest: function () {
        },

        deleteFriendRequest: function () {
        },

    };

    this.Friends = Friends;

})();