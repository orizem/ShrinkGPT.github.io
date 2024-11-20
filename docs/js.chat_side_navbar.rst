================
Chat Side Navbar
================

Chat Side Navbar Module
=======================

MSBO
----

1. **#msbo.click: EventListener**::  
   Toggles the `msb-x` class on the `#msb` element when the `#msbo` element is clicked.  

   .. code-block:: javascript

      /**
       * Toggles the 'msb-x' class on the '#msb' element when the '#msbo' element is clicked.
       * 
       * @event
       * @param {Event} event - The click event triggered on the '#msbo' element.
       */
      $(document).on('click', '#msbo', function(){
          $('#msb').toggleClass('msb-x');
      });


Edit Chat Name Button Hover
---------------------------

2. **.prev-chat.hover: EventListener**::  
   Displays the `.edit-chat-name` button when hovering over a `.prev-chat` element.  

   .. code-block:: javascript

      /**
       * Displays the '.edit-chat-name' button when hovering over a '.prev-chat' element.
       * 
       * @event
       * @param {Event} event - The hover event triggered on the '.prev-chat' element.
       */
      $('.prev-chat').hover(function() {
          $(this).find('.edit-chat-name').toggle();
      });


Delete Chat Button Hover
------------------------

3. **.prev-chat.hover: EventListener**::  
   Displays the `.delete-chat` button when hovering over a `.prev-chat` element.  

   .. code-block:: javascript

      /**
       * Displays the '.delete-chat' button when hovering over a '.prev-chat' element.
       * 
       * @event
       * @param {Event} event - The hover event triggered on the '.prev-chat' element.
       */
      $('.prev-chat').hover(function() {
          $(this).find('.delete-chat').toggle();
      });


Edit Chat Name Button Click
---------------------------

4. **.edit-chat-name.click: EventListener**::  
   Triggers the `editButtonLogic` function when the `.edit-chat-name` button is clicked.  

   .. code-block:: javascript

      /**
       * Triggers the 'editButtonLogic' function when the '.edit-chat-name' button is clicked.
       * 
       * @event
       * @param {Event} event - The click event triggered on the '.edit-chat-name' button.
       */
      $(".edit-chat-name").click(function () {
          editButtonLogic($(this));
      });


Delete Chat Button Click
------------------------

5. **.delete-chat.click: EventListener**::  
   Triggers the `deleteButtonLogic` function when the `.delete-chat` button is clicked.  

   .. code-block:: javascript

      /**
       * Triggers the 'deleteButtonLogic' function when the '.delete-chat' button is clicked.
       * 
       * @event
       * @param {Event} event - The click event triggered on the '.delete-chat' button.
       */
      $(".delete-chat").click(function () {
          deleteButtonLogic($(this));
      });


Name Input Key Press
--------------------

6. **.name_input.keypress: EventListener**::  
   Triggers the `editButtonLogic` function when the 'Enter' key is pressed while typing in the `.name_input` field.  

   .. code-block:: javascript

      /**
       * Triggers the 'editButtonLogic' function when the 'Enter' key is pressed while typing in the '.name_input' field.
       * 
       * @event
       * @param {Event} event - The keypress event triggered on the '.name_input' element.
       */
      $('.name_input').keypress(function(event) {
          if (event.which === 13) {
              editButtonLogic($(this).parent().find('.edit-chat-name'));
          }
      });


Edit Button Logic
-----------------

7. **editButtonLogic: Function**::  
   Handles the logic for editing the name of a chat.  
   Updates the input field's readonly state and border styles, and sends a GET request to update the chat name if it has been changed.  

   .. code-block:: javascript

      /**
       * Handles the logic for editing the name of a chat.
       * Updates the input field's readonly state and border styles, and sends a GET request to update the chat name if it has been changed.
       * 
       * @param {jQuery} elem - The element that triggered the edit action.
       */
      function editButtonLogic(elem) {
          var $a = elem.parent().find("a");
          var id = $a.attr("id");
          var name = $a.attr("name");
          var $span = elem;

          $a.attr('href', function(_, currentHref) {
              return currentHref === '#' ? `/get_chat/${id}` : '#';
          });

          if ($a.attr('href') === '#') {
              $a.find("input").css("border", "2px solid #8a8a8a");
              $a.find("input").css("border-radius", "4px");
              $a.find("input").prop("readonly", false);
          } else {                    
              $a.find("input").css("border", "none");
              $a.find("input").prop("readonly", true);
              new_name = $a.find("input").val()

              if (new_name != name) {
                  $.get("/chat-edit", { name: new_name, id: id });
                  $a.attr('name', new_name);
              }
          }
      }


Delete Button Logic
-------------------

8. **deleteButtonLogic: Function**::  
   Handles the logic for deleting a chat.  
   Removes the chat element from the DOM and sends a GET request to delete the chat.  

   .. code-block:: javascript

      /**
       * Handles the logic for deleting a chat.
       * Removes the chat element from the DOM and sends a GET request to delete the chat.
       * 
       * @param {jQuery} elem - The element that triggered the delete action.
       */
      function deleteButtonLogic(elem) {
          var $a = elem.parent().find("a");
          var $prev = $a.parent();
          var id = $a.attr("id");
          var $span = elem;

          $a.attr('href', function(_, currentHref) {
              return currentHref === '#' ? `/get_chat/${id}` : '#';
          });

          $prev.remove();

          $.get("/chat-delete", { id: id });
      }


Bar Icon Animate
----------------

9. **barIconAnimate: Function**::  
   Toggles the `change` class on the clicked icon to trigger animation.  

   .. code-block:: javascript

      /**
       * Toggles the 'change' class on the clicked icon to trigger animation.
       * 
       * @param {HTMLElement} x - The element that triggered the animation.
       */
      function barIconAnimate(x) {
          x.classList.toggle("change");
      }
