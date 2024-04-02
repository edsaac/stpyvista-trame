function sendMessageToStreamlitClient(type, data) {
    console.log(type, data);
    const outData = Object.assign({
        isStreamlitMessage: true,
        type: type,
    }, data);
    window.parent.postMessage(outData, '*');
}

const Streamlit = {
    setComponentReady: function () {
        sendMessageToStreamlitClient('streamlit:componentReady', { apiVersion: 1 });
    },
    setFrameHeight: function (height) {
        sendMessageToStreamlitClient('streamlit:setFrameHeight', { height: height });
    },
    setComponentValue: function (value) {
        sendMessageToStreamlitClient('streamlit:setComponentValue', { value: value });
        // sendMessageToStreamlitClient('streamlit:setComponentValue', {value});  
    },
    RENDER_EVENT: 'streamlit:render',
    events: {
        addEventListener: function (type, callback) {
            window.addEventListener('message', function (event) {
                if (event.data.type === type) {
                    event.detail = event.data;
                    callback(event);
                }
            });
        }
    }
}

function sendValue(value) {
    Streamlit.setComponentValue(value);
}

function onRender(event) {
    if (!window.rendered) {
        const { key } = event.detail.args;
        Streamlit.setFrameHeight(500);
        window.rendered = true;
    }
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
Streamlit.setFrameHeight();
