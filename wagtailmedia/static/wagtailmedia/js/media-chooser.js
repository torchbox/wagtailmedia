function createMediaChooser(id) {
    var chooserElement = $('#' + id + '-chooser');
    var mediaTitle = chooserElement.find('.title');
    var input = $('#' + id);
    var editLink = chooserElement.find('.edit-link');

    $('.action-choose', chooserElement).on('click', function() {
        ModalWorkflow({
            url: window.chooserUrls.mediaChooser,
            onload: MEDIA_CHOOSER_MODAL_ONLOAD_HANDLERS,
            responses: {
                mediaChosen: function(mediaData) {
                    input.val(mediaData.id);
                    mediaTitle.text(mediaData.title);
                    chooserElement.removeClass('blank');
                    editLink.attr('href', mediaData.edit_link);
                }
            }
        });
    });

    $('.action-clear', chooserElement).on('click', function() {
        input.val('');
        chooserElement.addClass('blank');
    });

    let state = null;
    /* define public API functions for the chooser */
    const chooser = {
        getState: () => state,
        getValue: () => state && state.id,
        setState: (mediaData) => {
            if (mediaData == null) {
                // return early
                return
            }
            input.val(mediaData.id);
            mediaTitle.text(mediaData.title);
            editLink.attr('href', mediaData.edit_link);
            chooserElement.removeClass('blank');
            state = mediaData;
        },
    };

    return chooser;
}
