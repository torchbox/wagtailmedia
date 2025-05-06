MEDIA_CHOOSER_MODAL_ONLOAD_HANDLERS = {
    'chooser': function(modal, jsonData) {
        const searchUrl = $('form.media-search', modal.body).attr('action');
        const searchInput = $('#id_q', modal.body);
        const resultsContainer = $('#search-results', modal.body);
        const collectionChooser = $('#collection_chooser_collection_id', modal.body);
        /* save initial page browser HTML, so that we can restore it if the search box gets cleared */
        const initialPageResultsHtml = resultsContainer.html();

        /* currentTag stores the tag currently being filtered on, so that we can
        preserve this when paginating */
        let currentTag;

        let request;

        function ajaxifyLinks (context) {
            $('a.media-choice', context).on('click', function(e) {
                modal.loadUrl(this.href);
                e.preventDefault();
            });

            $('.pagination a', context).on('click', function(e) {
                let params = {
                    collection_id: collectionChooser.val()
                };

                if (this.hasAttribute("data-page")) {
                    params['p'] = this.getAttribute("data-page");
                }
                else if (this.parentElement.classList.contains("prev") || this.parentElement.classList.contains("next")) {
                    const href = new URL(this.href);
                    params = Object.fromEntries(href.searchParams.entries());
                }

                const query = searchInput.val();
                if (query.length) {
                    params['q'] = query;
                }
                if (currentTag) {
                    params['tag'] = currentTag;
                }

                request = fetchResults(params);
                e.preventDefault();
            });

            $('a[data-ordering]', context).on('click', function(e) {
                request = fetchResults({
                    q: searchInput.val(),
                    collection_id: collectionChooser.val(),
                    ordering: this.dataset["ordering"]
                });
                e.preventDefault();
            });
        }

        function fetchResults(requestData) {
            return $.ajax({
                url: searchUrl,
                data: requestData,
                success(data) {
                    request = null;
                    resultsContainer.html(data);
                    ajaxifyLinks(resultsContainer);
                },
                error() {
                    request = null;
                },
            });
        }

        function search() {
            const query = searchInput.val();
            const collection_id = collectionChooser.val()
            if (query !== '' || collection_id !== '') {
                /* Searching causes currentTag to be cleared - otherwise there's
                no way to de-select a tag */
                currentTag = null;
                request = fetchResults({
                    q: query,
                    collection_id: collection_id
                });
            }
            else {
                /* search box is empty - restore original page browser HTML */
                resultsContainer.html(initialPageResultsHtml);
                ajaxifyLinks();
            }
            return false;
        }

        ajaxifyLinks(modal.body);
        initWMTabs();

        $('form.media-upload', modal.body).on('submit', function() {
            var formdata = new FormData(this);

            // Get the title field of the submitted form, not the first in the modal.
            const input = this.querySelector('#id_media-chooser-upload-title');
            if (!input.value) {
                if (!input.hasAttribute('aria-invalid')) {
                    input.setAttribute('aria-invalid', 'true');
                    const field = input.closest('[data-field]');
                    field.classList.add('w-field--error');
                    const errors = field.querySelector('[data-field-errors]');
                    const icon = errors.querySelector('.icon');
                    if (icon) {
                        icon.removeAttribute('hidden');
                    }
                    const errorElement = document.createElement('p');
                    errorElement.classList.add('error-message');
                    // Global function provided by Wagtail.
                    errorElement.innerHTML = gettext('This field is required.');
                    errors.appendChild(errorElement);
                }
                setTimeout(cancelSpinner, 500);
            } else {
                $.ajax({
                    url: this.action,
                    data: formdata,
                    processData: false,
                    contentType: false,
                    type: 'POST',
                    dataType: 'text',
                    success: modal.loadResponseText,
                    error: function(response, textStatus, errorThrown) {
                        message = jsonData['error_message'] + '<br />' + errorThrown + ' - ' + response.status;
                        $('#upload').append(
                            '<div class="help-block help-critical">' +
                            '<strong>' + jsonData['error_label'] + ': </strong>' + message + '</div>');
                    }
                });
            }

            return false;
        });

        $('form.media-search', modal.body).on('submit', search);

        searchInput.on('input', function() {
            if (request) {
                request.abort();
            }
            clearTimeout($.data(this, 'timer'));
            var wait = setTimeout(search, 200);
            $(this).data('timer', wait);
        });
        collectionChooser.on('change', search);
        $('a.suggested-tag').on('click', function() {
            currentTag = $(this).text();
            searchInput.val('');
            request = fetchResults({
                'tag': currentTag,
                collection_id: collectionChooser.val()
            });
            return false;
        });

        // Note: There are two inputs with `#id_title` on the page.
        // The page title and media title. Select the input inside the modal body.
        $('[name="media-chooser-upload-file"]', modal.body).each(function() {
            const fileWidget = $(this);
            fileWidget.on('change', function () {
                let titleWidget = $('#id_media-chooser-upload-title', fileWidget.closest('form'));
                if (titleWidget.val() === '') {
                    // The file widget value example: `C:\fakepath\media.jpg`
                    const parts = fileWidget.val().split('\\');
                    const filename = parts[parts.length - 1];
                    titleWidget.val(filename.replace(/\.[^.]+$/, ''));
                }
            });
        });

        /* Add tag entry interface (with autocompletion) to the tag field of the media upload form */
        $('[name="media-chooser-upload-tags"]', modal.body).each(function() {
           $(this).tagit({
                autocomplete: {source: jsonData['tag_autocomplete_url']}
            });
        });
    },
    'media_chosen': function(modal, jsonData) {
        modal.respond('mediaChosen', jsonData['result']);
        modal.close();
    },
    'select_format': function(modal) {
        $('form', modal.body).on('submit', function() {
            var formdata = new FormData(this);

            $.post(this.action, $(this).serialize(), modal.loadResponseText, 'text');

            return false;
        });
    }
};
