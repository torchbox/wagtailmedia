const React = window.React;
const ReactDOM = window.ReactDOM;
const Modifier = window.DraftJS.Modifier;
const EditorState = window.DraftJS.EditorState;
const AtomicBlockUtils = window.DraftJS.AtomicBlockUtils;

/**
 *  Choose a media file in this modal
 */
class WagtailMediaChooser extends window.draftail.ModalWorkflowSource {
    componentDidMount() {
        const { onClose, entityType, entity, editorState } = this.props;

        $(document.body).on('hidden.bs.modal', this.onClose);

        this.workflow = global.ModalWorkflow({
            url: `${window.chooserUrls.mediaChooser}?select_format=true`,
            onload: MEDIA_CHOOSER_MODAL_ONLOAD_HANDLERS,
            urlParams: {},
            responses: {
                mediaChosen: (data) => this.onChosen(data)
            },
            onError: (err) => {
                console.error("WagtailMediaChooser Error", err);
                onClose();
            },
        });
    }

    onChosen(data) {
        const { editorState, entityType, onComplete } = this.props;

        const content   = editorState.getCurrentContent();
        const selection = editorState.getSelection();

        const entityData = data;
        const mutability = 'IMMUTABLE';

        const contentWithEntity = content.createEntity(entityType.type, mutability, entityData);
        const entityKey         = contentWithEntity.getLastCreatedEntityKey();
        const nextState         = AtomicBlockUtils.insertAtomicBlock(editorState, entityKey, ' ');

        this.workflow.close();

        onComplete(nextState);
    }
}

// Constraints the maximum size of the tooltip.
const OPTIONS_MAX_WIDTH  = 300;
const OPTIONS_SPACING    = 70;
const TOOLTIP_MAX_WIDTH  = OPTIONS_MAX_WIDTH + OPTIONS_SPACING;

/**
 *	Places media thumbnail HTML in the Rich Text Editor
 */
class WagtailMediaBlock extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            showTooltipAt: null,
        };

        this.setState      = this.setState.bind(this);
        this.openTooltip   = this.openTooltip.bind(this);
        this.closeTooltip  = this.closeTooltip.bind(this);
        this.renderTooltip = this.renderTooltip.bind(this);
    }

    componentDidMount() {
        document.addEventListener('mouseup', this.closeTooltip);
        document.addEventListener('keyup', this.closeTooltip);
        window.addEventListener('resize', this.closeTooltip);
    }

    openTooltip(e) {
        const { blockProps } = this.props;
        const { entity, onRemoveEntity } = blockProps;
        const data = entity.getData();

        const trigger = e.target.closest('[data-draftail-trigger]');

        if (!trigger) return; // Click is within the tooltip

        const container = trigger.closest('[data-draftail-editor-wrapper]');

        if (container.children.length > 1) return;  // Tooltip already exists

        const containerRect = container.getBoundingClientRect();
        const rect = trigger.getBoundingClientRect();
        const maxWidth = trigger.parentNode.offsetWidth - rect.width;
        const direction = maxWidth >= TOOLTIP_MAX_WIDTH ? 'left' : 'top-left'; // Determines position of the arrow on the tooltip

        let top  = 0;
        let left = 0;

        if(direction == 'left'){
            left = rect.width + 50;
            top  = rect.top - containerRect.top + (rect.height / 2);
        }
        else if (direction == 'top-left'){
            top = rect.top - containerRect.top + rect.height;
        }

        this.setState({
            showTooltipAt: {
                container: container,
                top: top,
                left: left,
                width: rect.width,
                height: rect.height,
                direction: direction,
            }
        });
    }

    closeTooltip(e) {
        if(e.target.classList){
            if(e.target.classList.contains("Tooltip__button")){
                return; // Don't setState if the "Delete" button was clicked
            }
        }
        this.setState({ showTooltipAt: null });
    }

    /**
     * Returns either a tooltip "portal" element or null
     */
    renderTooltip(data) {
        const { showTooltipAt } = this.state;
        const { blockProps } = this.props;
        const { entity, onRemoveEntity } = blockProps;

        // No tooltip coords exist, don't show one
        if(!showTooltipAt) return null;

        let options = []
        if(data.autoplay) options.push("Autoplay");
        if(data.mute) options.push("Mute");
        if(data.loop) options.push("Loop");
        const options_str = options.length ? options.join(", ") : "";

        return ReactDOM.createPortal(React.createElement('div', null,
            React.createElement('div',
                {
                    style: {
                        top: showTooltipAt.top,
                        left: showTooltipAt.left
                    },
                    class: "Tooltip Tooltip--"+showTooltipAt.direction,
                    role:  "tooltip"
                },
                React.createElement('div', { style: { maxWidth: showTooltipAt.width } }, [
                    React.createElement('p', {
                        class: "ImageBlock__alt"
                    }, data.type.toUpperCase()+": "+data.title),
                    React.createElement('p', { class: "ImageBlock__alt" }, options_str),
                    React.createElement('button', {
                        class: "button button-secondary no Tooltip__button",
                        onClick: onRemoveEntity
                    }, "Delete")
                ])
            )
        ), showTooltipAt.container);
    }

    render() {
        const { blockProps } = this.props;
        const { entity } = blockProps;
        const data = entity.getData();

        let icon;
        if(data.type == 'video'){
            icon = React.createElement('span',  { class:"icon icon-fa-video-camera", 'aria-hidden':"true" });
        }
        else if(data.type == 'audio'){
            icon = React.createElement('span',  { class:"icon icon-fa-music", 'aria-hidden':"true" });
        }

        return React.createElement('button',
            {
                class: 'MediaBlock WagtailMediaBlock '+data.type,
                type:  'button',
                tabindex: '-1',
                'data-draftail-trigger': "true",
                onClick: this.openTooltip,
                style: { 'min-width': '100px', 'min-height': '100px'}
            },
            [
                React.createElement('span',
                    { class:"MediaBlock__icon-wrapper", 'aria-hidden': "true" },
                    React.createElement('span', {}, icon)
                ),
                React.createElement('img', { src: data.thumbnail }),
                this.renderTooltip(data)
            ]
        );
    }
}

window.draftail.registerPlugin({
    type: 'MEDIA',
    source: WagtailMediaChooser,
    block: WagtailMediaBlock
});
