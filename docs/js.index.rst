Index
=====

1. **DOMContentLoaded: EventListener**::  
   Initializes the table data and sets up the content update cycle.  
   Updates the content of the `#contentDiv` with review data every 5 seconds.  

   .. code-block:: javascript

      /**
       * Initializes the table data and sets up the content update cycle.
       * Updates the content of the `#contentDiv` with review data every 5 seconds.
       * 
       * @event
       * @param {Event} event - The DOMContentLoaded event that triggers the initial setup.
       */
      document.addEventListener('DOMContentLoaded', function () {
          const tableData = JSON.parse(`{{ reviews | safe }}`);
          let currentIndex = 0;

          function updateContent() {
              // Get the current row
              const currentRow = tableData[currentIndex];

              const baseImageUrl = "{{ url_for('views.get_image', username='') }}";
              const defaultImageUrl = "{{ url_for('static', filename='image/default.png') }}";

              const imageUrl = currentRow.user_id !== "null"
                  ? `${baseImageUrl}${encodeURIComponent(currentRow.name)}`
                  : defaultImageUrl;
              const image = `<img class="review_user_picture" src="${imageUrl}" alt="User Image">`;

              const TPL_Results = () => `<div class="Results-item">
                  <h3 class="">${currentRow.name}: ${currentRow.title}</h3>` + image + `
                  <p class="testimonial-text">${currentRow.content}</p>`;

              let reviewHTML = TPL_Results()

              // Loop through the total number of stars
              for (let i = 1; i <= currentRow.stars; i++) {
                  if (i <= currentRow.stars) {
                      // If the current index is less than or equal to the rating, use a filled star
                      reviewHTML += '<span class="star filled-star"></span>';
                  } else {
                      // Otherwise, use an empty star
                      reviewHTML += '<span class="star empty-star"></span>';
                  }
              }

              reviewHTML += `<p class="">${currentRow.submitted_at}</p></div>`;
                
              document.querySelector("#contentDiv").innerHTML = reviewHTML;

              // Move to the next index
              currentIndex = (currentIndex + 1) % tableData.length;
          }

          // Initial content update
          updateContent();
          // Update content every 5 second
          setInterval(updateContent, 5000);
      });
