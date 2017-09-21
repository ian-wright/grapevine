// module-level settings object
(function() {
    var s;
    var n;
    var Friends = {

        nodes: {
            addFriendButton: $("#add-friend-button"),
            addFriendEmail: $("#add-friend-email"),
            ajaxAlerts: $("#ajax-alerts")
        },

        settings: {
        },

        init: function () {
            // give easy access to settings for everything in module
            n = this.nodes;
            s = this.settings;
            this.bindUIActions();
        },

        bindUIActions: function () {
            n.addFriendButton.on("click", function () {
                Friends.addFriend(n.addFriendEmail.val());
            });
        },

        addFriend: function (email) {
            console.log("attempting to add friend:", email);
            var data = {email: email};
            $.ajax({
                type : "POST",
                url : "/add-friend",
                data: JSON.stringify(data),
                contentType: 'application/json;charset=UTF-8',
                success: function(resp) {
                    n.ajaxAlerts.text(resp);
                }
            });
        }

    };
    this.Friends = Friends;
})();