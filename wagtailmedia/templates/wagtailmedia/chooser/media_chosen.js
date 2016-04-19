function(modal) {
    modal.respond('mediaChosen', {{ media_json|safe }});
    modal.close();
}
