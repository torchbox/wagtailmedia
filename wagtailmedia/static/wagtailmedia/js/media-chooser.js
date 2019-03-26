function createMediaChooser(id) {
    var chooserElement = $('#' + id + '-chooser');
    var mediaTitle = chooserElement.find('.title');
    var input = $('#' + id);
    var editLink = chooserElement.find('.edit-link');

    $('.action-choose', chooserElement).click(function() {
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

    $('.action-clear', chooserElement).click(function() {
        input.val('');
        chooserElement.addClass('blank');
    });
}
