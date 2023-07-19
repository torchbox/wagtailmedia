function createMediaChooser(id) {
    const chooserElement = $('#' + id + '-chooser');
    const mediaTitle = chooserElement.find('[data-chooser-title]');
    const input = $('#' + id);

    let chooseAction = chooserElement.find('.action-choose');
    if (!chooseAction.length) {
        chooseAction = chooserElement.find('[data-chooser-action-choose]');
    }
    let clearAction = chooserElement.find('.action-clear');
    if (!clearAction.length) {
        clearAction = chooserElement.find('[data-chooser-action-clear]');
    }
    let editAction = chooserElement.find('.edit-link');
    if (!editAction.length) {
        editAction = chooserElement.find('[data-chooser-edit-link]');
    }


    chooseAction.on('click', function() {
        ModalWorkflow({
            url: chooserElement.data('chooserUrl'),
            onload: MEDIA_CHOOSER_MODAL_ONLOAD_HANDLERS,
            responses: {
                mediaChosen: function(mediaData) {
                    input.val(mediaData.id);
                    mediaTitle.text(mediaData.title);
                    chooserElement.removeClass('blank');
                    editAction.attr('href', mediaData.edit_url);
                    editAction.removeClass('w-hidden');
                }
            }
        });
    });

    clearAction.on('click', function() {
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
            editAction.attr('href', mediaData.edit_url);
            editAction.removeClass('w-hidden');
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
            chooseAction.focus();
        }
    };

    return chooser;
}
