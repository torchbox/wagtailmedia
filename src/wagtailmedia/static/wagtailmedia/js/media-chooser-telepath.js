(function() {
    function MediaChooser(html, idPattern) {
        this.html = html;
        this.idPattern = idPattern;
    }

    MediaChooser.prototype.render = function(placeholder, name, id, initialState) {
        const html = this.html.replace(/__NAME__/g, name).replace(/__ID__/g, id);
        // eslint-disable-next-line no-param-reassign
        placeholder.outerHTML = html;
        /* the chooser object returned by createMediaChooser also serves as the JS widget representation */
        // eslint-disable-next-line no-undef
        const chooser = createMediaChooser(id);
        chooser.setState(initialState);
        return chooser;
    };

    window.telepath.register('wagtailmedia.MediaChooser', MediaChooser);
})();
