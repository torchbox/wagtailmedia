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

    var state = null;
    /* define public API functions for the chooser */
    var chooser = {
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
        getTextLabel: (opts) => {
            if (!mediaTitle.text()) return '';
            var maxLength = opts && opts.maxLength,
                result = mediaTitle.text();
            if (maxLength && result.length > maxLength) {
                return result.substring(0, maxLength - 1) + '…';
            }
            return result;
        },
        focus: function() {
            $('.action-choose', chooserElement).focus();
        }
    };

    return chooser;
}
