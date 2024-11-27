====
Chat
====

Chat Module
===========

Custom Video Controls
---------------------

1. **muteBtn.click: `EventListener`**::  
   Toggles the mute/unmute state of the video when the muteBtn is clicked.  
   Updates the muteBtn icon accordingly.  

   .. code-block:: javascript

      /**
       * Toggles the mute/unmute state of the video when the muteBtn is clicked.
       * Updates the muteBtn icon accordingly.
       * 
       * @event
       * @param {Event} event - The click event triggered on the muteBtn.
       */
      muteBtn.addEventListener('click', () => {
          video.muted = !video.muted;
          muteBtn.innerHTML = video.muted ? '<i class="fas fa-volume-down"></i>' : '<i class="fas fa-volume-up"></i>';
      });


2. **video.timeupdate: `EventListener`**::  
   Updates the value of the seek bar as the video plays.  
   The seek bar value is updated based on the current time of the video relative to its duration.  

   .. code-block:: javascript

      /**
       * Updates the value of the seek bar as the video plays.
       * The seek bar value is updated based on the current time of the video relative to its duration.
       * 
       * @event
       * @param {Event} event - The timeupdate event triggered by the video element.
       */
      video.addEventListener('timeupdate', () => {
          seekBar.value = (video.currentTime / video.duration) * 100 || 0;
      });


3. **seekBar.input: `EventListener`**::  
   Allows the user to seek through the video by interacting with the seek bar.  
   Updates the video's currentTime based on the seek bar value.  

   .. code-block:: javascript

      /**
       * Allows the user to seek through the video by interacting with the seek bar.
       * Updates the video's currentTime based on the seek bar value.
       * 
       * @event
       * @param {Event} event - The input event triggered on the seekBar.
       */
      seekBar.addEventListener('input', () => {
          video.currentTime = (seekBar.value / 100) * video.duration;
      });


4. **fullscreenBtn.click: `EventListener`**::  
   Toggles the fullscreen state of the video when the fullscreenBtn is clicked.  
   Changes the fullscreenBtn icon depending on whether the video is in fullscreen mode.  

   .. code-block:: javascript

      /**
       * Toggles the fullscreen state of the video when the fullscreenBtn is clicked.
       * Changes the fullscreenBtn icon depending on whether the video is in fullscreen mode.
       * 
       * @event
       * @param {Event} event - The click event triggered on the fullscreenBtn.
       */
      fullscreenBtn.addEventListener('click', () => {
          if (!document.fullscreenElement) {
              video.requestFullscreen().catch(err => {
                  console.error(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
              });
              fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>'; // Change to compress icon
          } else {
              document.exitFullscreen();
              fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>'; // Change to expand icon
          }
      });



Drag & Drop Video
-----------------

1. **startDrag: `EventListener`**::  
   Initiates the dragging process when the user starts interacting with the `videoBox`.  
   Sets up the appropriate event listeners for mouse or touch events and disables transition during dragging.  

   .. code-block:: javascript

      /**
       * Initiates the dragging process when the user starts interacting with the videoBox.
       * Sets up the appropriate event listeners for mouse or touch events and disables transition during dragging.
       * 
       * @event
       * @param {Event} e - The event triggered by either a "mousedown" or "touchstart".
       */
      function startDrag(e) {
          e.preventDefault();
          isDragging = true;

          if (e.type === "mousedown") {
              offsetX = e.clientX - videoBox.getBoundingClientRect().left;
              offsetY = e.clientY - videoBox.getBoundingClientRect().top;
              document.addEventListener("mousemove", handleDrag);
              document.addEventListener("mouseup", stopDrag);
          } else if (e.type === "touchstart") {
              const touch = e.touches[0];
              offsetX = touch.clientX - videoBox.getBoundingClientRect().left;
              offsetY = touch.clientY - videoBox.getBoundingClientRect().top;
              document.addEventListener("touchmove", handleDrag);
              document.addEventListener("touchend", stopDrag);
          }

          videoBox.style.transition = "none"; // Disable transition while dragging
      }


2. **handleDrag: `EventListener`**::  
   Handles the dragging process as the user moves the mouse or touch across the screen.  
   Updates the position of `videoBox` and constrains its movement within the container's boundaries.  

   .. code-block:: javascript

      /**
       * Handles the dragging process as the user moves the mouse or touch across the screen.
       * Updates the position of videoBox and constrains its movement within the container's boundaries.
       * 
       * @event
       * @param {Event} e - The event triggered by either a "mousemove" or "touchmove".
       */
      function handleDrag(e) {
          if (!isDragging) return;

          let clientX, clientY;
          if (e.type === "mousemove") {
              clientX = e.clientX;
              clientY = e.clientY;
          } else if (e.type === "touchmove") {
              clientX = e.touches[0].clientX;
              clientY = e.touches[0].clientY;
          }

          const containerRect = videoBox.parentElement.getBoundingClientRect();
          let newLeft = clientX - offsetX - containerRect.left;
          let newTop = clientY - offsetY - containerRect.top;

          // Constrain within the container
          newLeft = Math.max(0, Math.min(containerRect.width - videoBox.offsetWidth, newLeft));
          newTop = Math.max(0, Math.min(containerRect.height - videoBox.offsetHeight, newTop));

          videoBox.style.left = `${newLeft}px`;
          videoBox.style.top = `${newTop}px`;
      }


3. **stopDrag: `EventListener`**::  
   Stops the dragging process and re-enables the transition on `videoBox`.  
   Removes the event listeners for mouse and touch events once the dragging ends.  

   .. code-block:: javascript

      /**
       * Stops the dragging process and re-enables the transition on videoBox.
       * Removes the event listeners for mouse and touch events once the dragging ends.
       * 
       * @event
       * @param {Event} e - The event triggered by either a "mouseup" or "touchend".
       */
      function stopDrag() {
          isDragging = false;
          videoBox.style.transition = "box-shadow 0.3s ease"; // Re-enable transition
          document.removeEventListener("mousemove", handleDrag);
          document.removeEventListener("mouseup", stopDrag);
          document.removeEventListener("touchmove", handleDrag);
          document.removeEventListener("touchend", stopDrag);
      }


Text To Speech
--------------

1. **toggleTextToSpeech: `Function`**::  
   Toggles the Text-to-Speech (TTS) playback when the associated button is clicked.  
   If the text is currently playing from the clicked button, it stops the playback. Otherwise, it stops any previous speech and starts the TTS from the clicked button.

   .. code-block:: javascript

      /**
       * Toggles the Text-to-Speech (TTS) playback when the associated button is clicked.
       * If the text is currently playing from the clicked button, it stops the playback.
       * Otherwise, it stops any previous speech and starts the TTS from the clicked button.
       * 
       * @event
       * @param {Event} event - The click event triggered on the TTS button.
       * @param {string} text - The text to be read aloud.
       */
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


2. **requestTextToSpeech: `Function`**::  
   Requests the browser to speak the provided text using the Speech Synthesis API.  
   Configures the voice, volume, rate, and pitch before speaking the text aloud. Also handles button state and audio controls.

   .. code-block:: javascript

      /**
       * Requests the browser to speak the provided text using the Speech Synthesis API.
       * Configures the voice, volume, rate, and pitch before speaking the text aloud.
       * Also handles button state and audio controls.
       * 
       * @param {HTMLElement} button - The button that triggered the text-to-speech action.
       * @param {string} text - The text to be read aloud.
       */
      function requestTextToSpeech(button, text) {
          try{
              stopTextToSpeech(); // Stop any previous audio
          }
          catch{}

          var msg = new SpeechSynthesisUtterance();
          var voices = window.speechSynthesis.getVoices();
          
          // Change the button text to "Stop TTS"
          button.innerText = '||';
          
          msg.voice = voices[10]; 
          msg.volume = 1; // From 0 to 1
          msg.rate = 1.8; // From 0.1 to 10
          msg.pitch = 2; // From 0 to 2
          msg.text = text;
          msg.lang = 'en';
          
          // When the utterance ends, capture the audio
          msg.onend = function(event) {
              button.innerText = "►";
              playingTarget = null;
          };
          
          // Speak the utterance
          speechSynthesis.speak(msg);
          
          // Play the audio
          audio.play();
      }


3. **stopTextToSpeech: `Function`**::  
   Stops the current Text-to-Speech playback and resets the audio state.  
   Resets the button text to "Start TTS" and clears the playing target.

   .. code-block:: javascript

      /**
       * Stops the current Text-to-Speech playback and resets the audio state.
       * Resets the button text to "Start TTS" and clears the playing target.
       * 
       * @param {HTMLElement} button - The button element that initiated the stop action.
       */
      function stopTextToSpeech(button) {
          speechSynthesis.cancel(); // Cancel the current speech synthesis
          audio.pause(); // Pause the audio element
          audio.currentTime = 0; // Reset the audio element

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

1. **navigator.mediaDevices.getUserMedia: `Function`**::  
   Requests access to the user's audio input device and initiates the recording process.  
   The audio stream is passed to the handler function once access is granted.

   .. code-block:: javascript

      /**
       * Requests access to the user's audio input device and initiates the recording process.
       * The audio stream is passed to the handler function once access is granted.
       * 
       * @event
       * @param {Object} options - The options for getting the media, specifying audio capture.
       * @param {Function} handlerFunction - The function to handle the audio stream.
       */
      navigator
          .mediaDevices
          .getUserMedia({audio: true})
          .then(stream => { handlerFunction(stream) });


2. **handlerFunction: `Function`**::  
   Initializes a MediaRecorder to record the audio stream.  
   When recording data is available, it pushes the data into an array. Once the recorder stops, the audio is converted into a Blob and sent via an AJAX request.

   .. code-block:: javascript

      /**
       * Initializes a MediaRecorder to record the audio stream.
       * When recording data is available, it pushes the data into an array.
       * Once the recorder stops, the audio is converted into a Blob and sent via an AJAX request.
       * 
       * @param {MediaStream} stream - The audio stream from the user's device.
       */
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


3. **sendData: `Function`**::  
   Sends the recorded audio data to the server via an AJAX POST request.  
   The audio is packaged into a FormData object before sending, and the response updates the text input field with the result.

   .. code-block:: javascript

      /**
       * Sends the recorded audio data to the server via an AJAX POST request.
       * The audio is packaged into a FormData object before sending.
       * The response updates the text input field with the result.
       * 
       * @param {Blob} data - The audio data to be sent to the server.
       */
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


4. **toggleRecording.onclick: `EventListener`**::  
   Toggles the start and stop of the audio recording when the associated button is clicked.  
   Updates the button's class and state based on whether recording is active or not.

   .. code-block:: javascript

      /**
       * Toggles the start and stop of the audio recording when the associated button is clicked.
       * Updates the button's class and state based on whether recording is active or not.
       * 
       * @event
       * @param {Event} event - The click event triggered on the toggleRecording button.
       */
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



Emoji Keyboard
--------------

1. **emojiBtn.addEventListener: `EventListener`**::  
   Toggles the visibility of the emoji picker when the emoji button is clicked.  
   If the emoji picker is visible, it is hidden; if it's hidden, it is shown.

   .. code-block:: javascript

      /**
       * Toggles the visibility of the emoji picker when the emoji button is clicked.
       * If the emoji picker is visible, it is hidden; if it's hidden, it is shown.
       * 
       * @event
       * @param {Event} event - The click event triggered on the emoji button.
       */
      emojiBtn.addEventListener('click', () => {
          emojiPicker.style.display = emojiPicker.style.display === 'none' || emojiPicker.style.display === '' ? 'grid' : 'none';
      });


2. **emojiGridCreation: `Function`**::  
   Dynamically creates the emoji grid from a list of emojis and appends each emoji to the emoji picker.  
   Each emoji is clickable and inserts the emoji into the chat input field when clicked.

   .. code-block:: javascript

      /**
       * Dynamically creates the emoji grid from a list of emojis and appends each emoji to the emoji picker.
       * Each emoji is clickable and inserts the emoji into the chat input field when clicked.
       */
      emojis.forEach(emoji => {
          const emojiElement = document.createElement('span');
          emojiElement.classList.add('emoji');
          emojiElement.textContent = emoji;
          emojiPicker.appendChild(emojiElement);

          /**
           * Inserts the selected emoji into the chat input field and hides the emoji picker.
           * 
           * @event
           * @param {Event} event - The click event triggered when an emoji is selected.
           */
          emojiElement.addEventListener('click', () => {
              chatInput.value += emoji; // Insert emoji into the textarea
              emojiPicker.style.display = 'none'; // Close the emoji picker after selection
          });
      });


3. **document.addEventListener: `EventListener`**::  
   Closes the emoji picker if the user clicks outside of it.  
   The emoji picker is hidden when a click occurs outside both the emoji button and the emoji picker.

   .. code-block:: javascript

      /**
       * Closes the emoji picker if the user clicks outside of it.
       * The emoji picker is hidden when a click occurs outside both the emoji button and the emoji picker.
       * 
       * @event
       * @param {Event} event - The click event triggered when the user clicks anywhere on the document.
       */
      document.addEventListener('click', (e) => {
          if (!emojiBtn.contains(e.target) && !emojiPicker.contains(e.target)) {
              emojiPicker.style.display = 'none';
          }
      });

4. **emojis: `const`**::  
   The emojis included in keyboard.

   .. code-block:: javascript

        '🧝', '👻', '🕵️', '💅', '😟', '🤑', '☠️', '😓', '👩', '👯',
        '😒', '🤵', '😛', '🤬', '👩', '🌞', '👳', '🛀', '😣', '😘',
        '😙', '🧙', '😡', '🤫', '🧒', '👩', '😖', '💇', '🤳', '🦋',
        '🤩', '👿', '✨', '👩', '☹️', '🧝', '🌱', '🧙', '😄', '😢',
        '🕺', '😃', '😅', '💄', '🧛', '🌸', '🙃', '🧠', '💂', '👦',
        '🤒', '😊', '💊', '😗', '🧚', '👩', '👵', '💩', '👨', '👩',
        '😫', '🥳', '💂', '👰', '🤭', '😜', '🤔', '👧', '👹', '💉',
        '🧔', '🙂', '💀', '🤧', '👲', '🥰', '🧖', '🧴', '🤣', '🌈',
        '😍', '👯', '🧓', '🤕', '💆', '🤗', '💋', '😀', '🛋️', '👷',
        '👨', '👨', '😈', '😂', '😉', '🏨', '😆', '😋', '🤡', '👀',
        '🙁', '😔', '👶', '👷', '💇', '😝', '👨', '👮', '💆', '🏥',
        '🧖', '🧘', '😌', '😚', '👨', '🌟', '👮', '🧑', '🧛', '👴',
        '👩', '👨', '😩', '👺', '👨', '👩', '😏', '🩹', '😁', '💃',
        '🕴️', '👳', '😭', '🧜', '👱', '😞', '😠', '🧜', '🧸', '🧑',
        '👨', '👱', '😇', '💍', '👨', '🏩', '😤', '👨', '🕊️', '😕',
        '😎', '😥', '🩺', '🕵️', '👩', '🧘', '👩', '🧝'


Additional Functions
--------------------

1. **appendMessage: Function**::  
   Appends a message to the chat window, including the sender's name, image, text, time, and an optional video URL.  
   It also handles the rendering of the text-to-speech button for the message.  

   .. code-block:: javascript

      /**
       * Appends a message to the chat window, including the sender's name, image, text, time, and an optional video URL.
       * It also handles the rendering of the text-to-speech button for the message.
       * 
       * @param {string} name - The name of the sender.
       * @param {string} img - The image URL for the sender's avatar.
       * @param {string} side - The side of the chat (either "left" or "right").
       * @param {string} [text=""] - The message text to be displayed.
       * @param {string} time - The time the message was sent.
       * @param {string} [videoURL=""] - The URL for an optional video to be displayed (if any).
       */
      function appendMessage(name, img, side, text="", time, videoURL="") {
        const msgHTML = `
          <div class="msg ${side}-msg">
            <div class="msg-img" style="background-image: url(${img})"></div>
            <div class="msg-bubble">
              <div class="msg-info">
                <div class="msg-info-name">${name}</div>
                <div class="msg-info-time">${time}</div>
              </div>
              <div class="msg-text" style="word-break: break-all;">${text}</div>
              <div style="text-align: right; font-size:10pt;">
                <button id="btn-tts" style="text-align: center; background-color: transparent; color: black; border-radius: 100%; width: 20pt; height:20pt;" onclick="toggleTextToSpeech(event, '${text.replace(/\"/g, "").replace(/\'/g, "")}')">►</button>
              </div>
            </div>
          </div>
        `;
        msgerChat.insertAdjacentHTML("beforeend", msgHTML);
        msgerChat.scrollTop += 500;

        if (videoURL) {
          var video = document.getElementById('videoFrame');
          var source = document.getElementById('videoSource');
          source.src = videoURL;
          video.muted = false;
          video.loop = false;
          video.load();
          video.play();
        }
      }

2. **myHandler: EventListener**::  
   Handles the 'ended' event of the avatar video and sets it to a default idle state.  
   The video is switched to a default idle video and played again when the avatar video ends.  

   .. code-block:: javascript

      /**
       * Handles the 'ended' event of the avatar video and sets it to a default idle state.
       * The video is switched to a default idle video and played again when the avatar video ends.
       * 
       * @event
       * @param {Event} e - The 'ended' event triggered when the avatar video finishes playing.
       */
      function myHandler(e) {
        var video = document.getElementById('videoFrame');
        var source = document.getElementById('videoSource');
        source.src = "../static/video/emma_idle.mp4";
        video.muted = false;
        video.loop = false;
        video.load();
        video.play();
      }

3. **botResponse: Function**::  
   Handles the bot's response based on the user's input message.  
   It fetches the bot's response from the server and appends it to the chat, along with any video URL (if applicable).  

   .. code-block:: javascript

      /**
       * Handles the bot's response based on the user's input message.
       * It fetches the bot's response from the server and appends it to the chat, along with any video URL (if applicable).
       * 
       * @param {string} rawText - The raw input text from the user that triggers the bot's response.
       */
      function botResponse(rawText) {
        dateTime = formatDate(new Date());
        $.get("/get", { msg: rawText, firstTime: firstTime, dateTime: dateTime, chatId: chatId }).done(function (response) {
          if (firstTime == 1) {
            firstTime = 0;
          }
          const msgText = response.encoded_bot_response;
          const msgVideo = response.avatar_video_url;
          appendMessage(BOT_NAME, BOT_IMG, "left", msgText, dateTime, msgVideo);
        });
      }

4. **get: Function**::  
   A utility function to select an element based on a given CSS selector.  

   .. code-block:: javascript

      /**
       * A utility function to select an element based on a given CSS selector.
       * 
       * @param {string} selector - The CSS selector to query the DOM.
       * @param {Element} [root=document] - The root element to query within (defaults to the document).
       * @returns {Element} The DOM element that matches the selector.
       */
      function get(selector, root = document) {
        return root.querySelector(selector);
      }

5. **formatDate: Function**::  
   Formats a Date object into a time string in the format of 'HH:MM'.  

   .. code-block:: javascript

      /**
       * Formats a Date object into a time string in the format of 'HH:MM'.
       * 
       * @param {Date} date - The Date object to be formatted.
       * @returns {string} The formatted time string in the format 'HH:MM'.
       */
      function formatDate(date) {
        let hours = date.getHours();
        let minutes = date.getMinutes();
        return `${hours}:${minutes < 10 ? '0' + minutes : minutes}`;
      }