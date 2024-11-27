===================
Important Function
===================

Chat
----

.. tabs::

    .. tab:: Backend

        .. code-block:: python

            @views.route("/get", endpoint="get")
            @restricted_route_decorator(check_session=False)
            def get_bot_response():
                """Handle GET request for bot response.

                Process user input and generate a response from the AI model.

                Returns
                -------
                    dict: A dictionary containing the encoded bot response and avatar video URL.

                Note
                ----
                    This endpoint requires authentication and appropriate permissions.
                """
                from .models import db

                user = get_current_user()
                chat_id = int(request.args.get("chatId"))
                first_time = request.args.get("firstTime")
                user_msg = request.args.get("msg")
                date_time = request.args.get("dateTime")

                if chat_id != -1:
                    current_chat = Chat.query.filter_by(user_id=current_user.id, id=chat_id).first()
                elif user.status == 1:
                    welcome_text = ""
                    welcome_response = {
                        "identifier": "assistant",
                        "text": welcome_text,
                        "date_time": date_time,
                    }
                    new_chat = Chat(
                        name=f"Chat_{len(user.chats)}",
                        chat_json=dumps([welcome_response]),
                        user_id=current_user.id,
                    )
                    db.session.add(new_chat)
                    db.session.commit()
                    current_chat = user.chats[-1]
                else:
                    if first_time == "1":
                        if user.status == 1:
                            welcome_text = QUESTIONS[0].format(user.full_name) + "\n" + QUESTIONS[1]
                        else:
                            welcome_text = f"Hi { user.name.title() }, welcome to Shrink.io! Go ahead and send me a message."

                        welcome_response = {
                            "identifier": "assistant",
                            "text": welcome_text,
                            "date_time": date_time,
                        }
                        new_chat = Chat(
                            name=f"Chat_{len(user.chats)}",
                            chat_json=dumps([welcome_response]),
                            user_id=current_user.id,
                        )
                        db.session.add(new_chat)
                        db.session.commit()
                    current_chat = user.chats[-1]

                existing_messages = current_chat.chat
                new_message = {"identifier": "user", "text": user_msg, "date_time": date_time}
                existing_messages.append(new_message)

                if user.status == 0:
                    chat_history = [
                        format_chat_history_for_gpt(__chat) for __chat in existing_messages
                    ]

                    db_chats_history = get_previous_chats(user)

                    # Prepare messages for OpenAI API
                    messages = GPT_MESSAGES + db_chats_history + chat_history

                    # Interact with OpenAI GPT-4
                    response = client.chat.completions.create(model="gpt-4o", messages=messages)
                    bot_response = response.choices[0].message.content
                else:
                    bot_response = get_initial_chat_state_response(user)

                new_message = {"identifier": "assistant", "text": bot_response, "date_time": date_time}
                existing_messages.append(new_message)

                current_chat.chat = existing_messages

                # Update chat history
                db.session.add(current_chat)
                db.session.commit()

                encoded_bot_response = html_encode(bot_response)

                # Generate response avatar stream
                try:      
                    API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
                    token = os.environ.get("HUGGINGFACE_API_KEY")
                    headers = {"Authorization": token}
                    payload = {
                        "inputs": user_msg,
                    }
                    
                    try:
                        response = requests.post(API_URL, headers=headers, json=payload)
                        res = response.json()[0]
                        
                        # Filter scores for list_labels
                        emotions = ["surprise", "joy", "neutral"]
                        filtered_data = [item for item in res if item['label'] in emotions]
                        
                        if filtered_data:
                            highest_score_label = max(filtered_data, key=lambda x: x['score'])['label']
                            emotion = highest_score_label
                            if emotion == "joy":
                                emotion = "happy"
                        else:
                            emotion = "neutral"
                    except Exception:    
                        emotion = "neutral"
                        
                    avatar_video_url = get_avatar_video(bot_response, emotion)
                except Exception as e:
                    print("[D-ID Video Error]:", e)
                    avatar_video_url = ""
                print("[avatar_video_url]:", avatar_video_url)

                response = {
                    "encoded_bot_response": encoded_bot_response,
                    "avatar_video_url": avatar_video_url,
                    "emotion": emotion,
                }

                return response


Text To Speech
--------------

.. tabs::

   .. tab:: Frontend

        .. code-block:: javascript

            var audio = new Audio();
            var playingTarget = null;

            function toggleTextToSpeech(event, text) {
                var button = event.target; // Get the button element that was clicked

                if (playingTarget === button) {
                    stopTextToSpeech(button);
                } else {
                    if (playingTarget)
                        stopTextToSpeech(playingTarget);

                    playingTarget = button
                    requestTextToSpeech(button, text);
                }
            }

            function requestTextToSpeech(button, text) {
                try{
                    stopTextToSpeech(); // Stop any previous audio
                }
                catch{}

                const synth = window.speechSynthesis;

                var msg = new SpeechSynthesisUtterance(text);
                var voices = synth.getVoices();
                
                // Change the button text to "Stop TTS"
                button.innerText = '||';
                
                function getVoices() {
                    voices = synth.getVoices();
                    if (voices.length === 0) {
                        synth.onvoiceschanged = function() {
                            voices = synth.getVoices();
                            setVoice(); 
                        };
                    } else {
                        setVoice(); 
                    }
                }
                
                function setVoice() {
                    msg.volume = 1; 
                    msg.lang = 'en-US'; // Enforcing a specific locale

                    var userAgent = navigator.userAgent;

                    if (userAgent.indexOf('Edg') !== -1) {
                        // Edge-specific adjustments
                        msg.rate = 1.2; // Slightly slower rate for Edge (if needed)
                        msg.pitch = 2; // Set pitch to normal for Edge
                        msg.voice = voices[2];
                    } else if (navigator.brave) {
                        // Brave-specific adjustments
                        msg.rate = 1; // Set rate to normal for Brave
                        msg.pitch = 2; // Set pitch to normal for Brave
                        msg.voice = voices[2];
                    } else {
                        // Default for other browsers
                        msg.rate = 1; // Normal speed for others
                        msg.pitch = 1; // Normal pitch for others
                        msg.voice = voices[5];
                    }

                    synth.speak(msg);
                }
                
                getVoices();
                
                // When the utterance ends, capture the audio
                msg.onend = function(event) {
                    button.innerText = "►";
                    playingTarget = null;
                };
                
                // Play the audio
                audio.addEventListener('play', () => {
                    console.log('Audio started playing');
                });
            }

            // Ensure that play requests are not interrupted by simultaneous pause calls
            function playAudio() {
                // Check if the audio is already playing
                if (audio.paused && !audio.ended) {
                    audio.play().catch((error) => {
                        console.error('Error during play:', error); // Catch and log any errors from the play request
                    });
                }
            }

            function stopTextToSpeech(button) {
                speechSynthesis.cancel(); // Cancel the current speech synthesis
                
                // Check if the audio is playing before pausing it
                if (!audio.paused) {
                    audio.pause(); // Pause the audio element
                    audio.currentTime = 0; // Reset the audio element
                }

                if (button){
                    // Change the button text to "Start TTS"
                    button.innerText = '►';
                    playingTarget = null;
                }
                else{
                    var buttons = document.querySelectorAll('#btn-tts');
                    
                    // Loop through each button and log its text content
                    buttons.forEach(function(button) {
                        button.innerText = "►"
                    });
                }
            }


Record Voice Message With Speech To Text
----------------------------------------

.. tabs::

    .. tab:: Frontend

        .. code-block:: javascript

            navigator
                .mediaDevices
                .getUserMedia({audio: true})
                .then(stream => { handlerFunction(stream) })
                .catch(error => {
                    console.log("Permission denied or another error occurred:", error);
                });

            function handlerFunction(stream) {
                rec = new MediaRecorder(stream);
                rec.ondataavailable = e => {
                    audioChunks.push(e.data);
                    if (rec.state == "inactive") {
                        let blob = new Blob(audioChunks, {type: 'audio/mpeg-3'});
                        sendData(blob);
                    }
                }
            }

            function sendData(data) {
                var form = new FormData();
                form.append('file', data, 'data.mp3');  // Ensure 'data' is a valid File object

                $.ajax({
                    type: 'POST',
                    url: '/save_record',
                    data: form,
                    cache: false,
                    processData: false,
                    contentType: false
                }).done(function(response) {
                    const resultText = response.text;
                    const textInput = document.getElementById('textInput');
                    if (textInput) {
                        textInput.value = resultText;
                    } else {
                        console.error("Textarea not found");
                    }
                }).fail(function(xhr, status, error) {
                    console.error('Error processing the file:', xhr.responseText || error);
                });
            }

            const toggleRecording = document.getElementById('toggleRecording');
            let isRecording = false;
            let audioChunks = [];

            toggleRecording.onclick = () => {
                if (isRecording) {
                    // Stop recording
                    console.log("Recording stopped.");
                    toggleRecording.classList.remove('recording');
                    rec.stop();
                } else {
                    // Start recording
                    console.log("Recording started.");
                    toggleRecording.classList.add('recording');
                    audioChunks = [];
                    rec.start();
                }
                isRecording = !isRecording;
            };

    .. tab:: Backend

        .. code-block:: python

            @views.route("/save_record", methods=["POST"])
            def save_record() -> tuple:
                """Audio File Transcription Endpoint

                This endpoint accepts audio file uploads and transcribes them to text.
                The audio file should be sent as a multipart form data with key 'file'.
                Only allowed audio file formats (as determined by allowed_file()) will be processed.
                The audio data is processed in memory without saving to disk.

                Returns
                -------
                tuple
                    A tuple containing two elements:
                    - First element: Either a JSON response with transcribed text or an error message string
                    - Second element: HTTP status code (200 for success, 400 for errors)

                Example Response
                ----------------
                Success: ({"text": "transcribed text content"}, 200)
                Error: ("No file part", 400) or ("Invalid file type", 400)
                """
                if "file" not in request.files:
                    return "No file part", 400

                file = request.files["file"]

                if file and allowed_file(file.filename):
                    file_bytes_data = file.read()
                    buffer = io.BytesIO(file_bytes_data)  # Read file data into memory
                    buffer.name = "file.mp3"
                    transcription = transcribe_audio(buffer)  # Transcribe the audio in memory
                    return jsonify({"text": transcription}), 200
                else:
                    return "Invalid file type", 400


            def transcribe_audio(file_bytes: io.BytesIO) -> str:
                """Transcribe Audio to Text using OpenAI's Whisper Model

                This function takes an audio file in bytes format and transcribes it to text
                using OpenAI's Whisper ASR (Automatic Speech Recognition) model.
                The file pointer is reset to the start before processing to ensure
                complete file reading.

                Parameters
                ----------
                file_bytes : io.BytesIO
                    A BytesIO object containing the audio data to be transcribed.
                    The audio should be in a format supported by the Whisper model
                    (e.g., mp3, wav, m4a, etc.).

                Returns
                -------
                str
                    The transcribed text from the audio file.
                    Returns an empty string if transcription fails.

                Notes
                -----
                - Uses OpenAI's 'whisper-1' model for transcription
                - Currently set to transcribe English language content only
                - Requires valid OpenAI API credentials in the client object

                Raises
                ------
                Exception
                    May raise exceptions related to API calls, invalid audio format,
                    or authentication issues with the OpenAI client.
                """
                file_bytes.seek(0)  # Reset pointer to the start of the file
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", file=file_bytes, language="en"
                )
                return transcription.text


D-ID Avater
-----------

.. tabs::

    .. tab:: Frontend

        .. code-block:: javascript

            // ============= [ D-ID Avater Default State ] ===============
            document.getElementById('videoFrame').addEventListener('ended',myHandler,false);
            function myHandler(e) {
                var video = document.getElementById('videoFrame');
                var source = document.getElementById('videoSource');
                
                source.src = "../static/video/emma_idle.mp4";
                video.muted = false;
                video.loop = false;
                video.load();
                video.play();
            }
            // ============= [ End D-ID Avater Default State ] ===============

            const msgerForm = get(".msger-inputarea");
            const msgerInput = get(".msger-input");
            const msgerChat = get(".msger-chat");


            // Icons made by Freepik from www.flaticon.com
            const BOT_IMG = "https://visualpharm.com/assets/825/Bot-595b40b65ba036ed117d3818.svg";
            const PERSON_IMG = "{{ url_for('views.get_image', username=user.username) }}";
            const BOT_NAME = "Shrink.io";
            const PERSON_NAME = "You";
            firstTime = 1;
            chatId = -1;

            // Load previous chats
            messages = {{ chat_data|tojson|safe }};
            if (messages != -1) {
                chatId = {{ chat_id }};

                for (var chat of messages) {
                if (["assistant", "bot"].includes(chat.identifier)) {
                    var name =  BOT_NAME;
                    var img = BOT_IMG;
                    var side = "left";
                }
                else {
                    var name =  PERSON_NAME;
                    var img = PERSON_IMG;
                    var side = "right";
                }
                appendMessage(name, img, side, chat.text, chat.date_time);
                }
            }

            msgerForm.addEventListener("submit", event => {
                event.preventDefault();

                const msgText = msgerInput.value;
                if (!msgText) return;

                appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText, formatDate(new Date()));
                msgerInput.value = "";
                botResponse(msgText);
            });


            // ============= [ Play D-ID Avater Stream ] ===============
            if (videoURL) {

                var video = document.getElementById('videoFrame');
                var source = document.getElementById('videoSource');
                // video.pause();

                source.src = videoURL;
                video.muted = false;
                video.loop = false;
                video.load();
                video.play();
            }

            // ============= [ End Play D-ID Avater Stream ] ===============
    
    .. tab:: Backend

        .. code-block:: python

            def get_avatar_video(text, emotion):
                """Generate an avatar video with a given emotion and text

                This function interacts with the D-ID API to generate a video where
                a given avatar speaks the provided text with the specified emotion.
                It returns the URL of the generated video.

                Parameters
                ----------
                text : str
                    The text that the avatar will speak.
                emotion : str
                    The emotion (e.g., "happy", "sad") to apply to the avatar's expression.

                Returns
                -------
                str
                    The URL of the generated avatar video.

                Examples
                --------
                >>> get_avatar_video("Hello, how are you?", "happy")
                'https://api.d-id.com/talks/xyz/result.mp4'
                """
                load_dotenv()
                D_ID_API_KEY = os.environ.get("D_ID_API_KEY")

                payload = {
                    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Emma_f/thumbnail.jpeg",
                    "script": {
                        "type": "text",
                        "input": text,
                        "provider": {
                            "type": "microsoft",
                            "voice_id": "en-US-JennyNeural",
                        },
                    },
                    "config": {
                        "driver_expressions": {
                            "expressions": [
                                {"start_frame": 0, "expression": f"{emotion}", "intensity": 1}
                            ]
                        }
                    },
                }
                headers = {
                    "accept": "application/json",
                    "Authorization": f"Basic {D_ID_API_KEY}",
                    "content-type": "application/json",
                }
                url = "https://api.d-id.com/talks"

                talks_response_json = dict()

                talks_response = requests.post(url, json=payload, headers=headers)
                talks_response_json = talks_response.json()

                url = url + "/" + talks_response_json.get("id")
                sleep(7)

                response = requests.get(url, headers=headers)
                response_json = response.json()

                return response_json.get("result_url")

Util Decorator
--------------

.. tabs::

    .. tab:: Backend

        .. code-block:: python

            def restricted_route_decorator(check_session: bool):
                """Restricted Route Decorator

                Check if the user session is valid, if not,
                it redirected to 404.
                In addition, the decorator check if the user exists,
                if not, will be redirected to index page.

                Must define endpoint for each route using this decorator.
                The decorator should be right above the function in
                order to run properly.

                Parameters
                ----------
                func : Callable
                    The function to wrap with authentication checking.
                """

                def decorator(func: Callable):
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        if check_session:
                            if "username" not in session:
                                return redirect(url_for("views.index"))
                            user = User.query.filter_by(username=session["username"]).first()

                            if user is None:
                                return redirect(url_for("views.index"))
                        else:
                            if (current_user is None) or (not current_user.is_authenticated):
                                msg = "The page you where looking for could not be found."
                                return render_template("404.html", err_msg=msg), 404
                            user = get_current_user()

                            if user is None:
                                return redirect(url_for("views.index"))

                        res = func(*args, **kwargs)
                        return res

                    return wrapper

                return decorator


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


