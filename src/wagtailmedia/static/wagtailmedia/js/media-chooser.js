function createMediaChooser(id) {
    const chooserElement = $('#' + id + '-chooser');
    const mediaTitle = chooserElement.find('.title');
    const input = $('#' + id);
    const editLink = chooserElement.find('.edit-link');
    const chooserBaseUrl = chooserElement.data('chooserUrl');

    $('.action-choose', chooserElement).on('click', function() {
        ModalWorkflow({
            url: chooserBaseUrl,
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
        getState: function() { return state; },
        getValue: function() {
            if (state) {
                return state.id;
            }
        },
        setState: function(mediaData) {
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
        getTextLabel: function(opts) {
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
