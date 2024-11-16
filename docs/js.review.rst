Review
======

1. **updateStars: Function**::  
   Updates the star rating display when the user clicks or hovers over a star.  
   Sets the appropriate filled or empty star class based on the clicked or hovered index.  

   .. code-block:: javascript

      /**
       * Updates the star rating display when the user clicks or hovers over a star.
       * Sets the appropriate filled or empty star class based on the clicked or hovered index.
       * 
       * @param {number} clickedIndex - The index of the clicked or hovered star.
       */
      function updateStars(clickedIndex) {
          const starInputs = document.querySelectorAll('.star-rating input[type="radio"]');
          starInputs.forEach((input, index) => {
              const label = input.nextElementSibling;
              const starSpan = label.querySelector('.star');
              if (index <= clickedIndex) {
                  starSpan.classList.remove('empty-star');
                  starSpan.classList.add('filled-star');
              } else {
                  starSpan.classList.remove('filled-star');
                  starSpan.classList.add('empty-star');
              }
          });
      }


2. **showTooltip: Function**::  
   Displays a tooltip when the user hovers over a star, showing the star rating.  

   .. code-block:: javascript

      /**
       * Displays a tooltip when the user hovers over a star.
       * Shows the star rating in the tooltip.
       * 
       * @param {Element} label - The label element containing the star.
       * @param {number} index - The index of the hovered star.
       */
      function showTooltip(label, index) {
          const tooltip = label.querySelector('.star-tooltip');
          tooltip.textContent = `${index + 1} star${index === 0 ? '' : 's'}`;
          tooltip.style.display = 'block';
      }


3. **hideTooltip: Function**::  
   Hides the tooltip when the mouse leaves the star.  

   .. code-block:: javascript

      /**
       * Hides the tooltip when the mouse leaves the star.
       * 
       * @param {Element} label - The label element containing the star.
       */
      function hideTooltip(label) {
          const tooltip = label.querySelector('.star-tooltip');
          tooltip.style.display = 'none';
      }


4. **label.addEventListener('click'): EventListener**::  
   Updates the star rating when a star is clicked.  
   Sets the associated radio button as checked.  

   .. code-block:: javascript

      /**
       * Updates the star rating when a star is clicked.
       * Sets the associated radio button as checked.
       * 
       * @event
       * @param {Event} event - The click event triggered on the star label.
       */
      starLabels.forEach((label, index) => {
          label.addEventListener('click', function(event) {
              event.preventDefault(); // Prevent the default action
              updateStars(index - 1); // Set stars based on clicked index
              const associatedInput = document.querySelector('#' + this.getAttribute('for'));
              associatedInput.checked = true; // Manually set the radio button as checked
          });
      });


5. **label.addEventListener('mouseenter'): EventListener**::  
   Displays the tooltip and highlights the stars when hovered over.  

   .. code-block:: javascript

      /**
       * Displays the tooltip and highlights the stars when hovered over.
       * 
       * @event
       * @param {Event} event - The mouseenter event triggered on the star label.
       */
      starLabels.forEach((label, index) => {
          label.addEventListener('mouseenter', function() {
              updateStars(index - 1);
              showTooltip(this, index);
          });
      });


6. **label.addEventListener('mouseleave'): EventListener**::  
   Removes the tooltip and resets the star rating when the mouse leaves the star.  

   .. code-block:: javascript

      /**
       * Removes the tooltip and resets the star rating when the mouse leaves the star.
       * 
       * @event
       * @param {Event} event - The mouseleave event triggered on the star label.
       */
      starLabels.forEach((label, index) => {
          label.addEventListener('mouseleave', function() {
              const checkedInput = document.querySelector('.star-rating input[type="radio"]:checked');
              const checkedIndex = checkedInput ? Array.from(starLabels).indexOf(checkedInput.nextElementSibling) : -1;
              updateStars(checkedIndex - 1); // Revert to the last selected stars
              hideTooltip(this);
          });
      });
