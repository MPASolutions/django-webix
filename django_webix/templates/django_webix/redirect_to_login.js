webix.modalbox({
    title: "{{_("User is not authenticated")|escapejs}}",
    buttons: ["OK"],
    width: 500,
    text: "{{_("You are no longer authenticated, please login again.")|escapejs}}"
}).then(function (result) {
    loading("{{ login_url }}");
});
