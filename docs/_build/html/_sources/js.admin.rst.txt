Admin
=====

Functions Used In Admin page
----------------------------

1. **$(".test-data-btn").click: EventListener**::  
   Sends a POST request to generate test data when the test data button is clicked.  
   After the request is successful, the page is redirected to the admin dashboard.

   .. code-block:: javascript

      /**
       * Sends a POST request to generate test data when the test data button is clicked.
       * After the request is successful, the page is redirected to the admin dashboard.
       * 
       * @event
       * @param {Event} event - The click event triggered on the test-data-btn.
       */
      $(".test-data-btn").click(function() {
          $.ajax({
              url: "/generate_test_data",
              type: "POST",
              success: function() {
                  window.location.href = "/admin_dashboard";
              }
          });
      });


2. **$(".delete-btn").click: EventListener**::  
   Sends a POST request to delete a user based on the user ID when the delete button is clicked.  
   After the request is successful, the page is redirected to the admin dashboard.

   .. code-block:: javascript

      /**
       * Sends a POST request to delete a user based on the user ID when the delete button is clicked.
       * After the request is successful, the page is redirected to the admin dashboard.
       * 
       * @event
       * @param {Event} event - The click event triggered on the delete-btn.
       */
      $(".delete-btn").click(function() {
          var userId = $(this).data("user-id");
          $.ajax({
              url: "/delete/" + userId,
              type: "POST",
              success: function() {
                  window.location.href = "/admin_dashboard";
              }
          });
      });


3. **$(".active-btn").click: EventListener**::  
   Sends a POST request to activate or deactivate a user based on the user ID and current user state.  
   After the request is successful, the page is redirected to the admin dashboard.

   .. code-block:: javascript

      /**
       * Sends a POST request to activate or deactivate a user based on the user ID and current user state.
       * After the request is successful, the page is redirected to the admin dashboard.
       * 
       * @event
       * @param {Event} event - The click event triggered on the active-btn.
       */
      $(".active-btn").click(function() {
          var userId = $(this).data("user-id");
          var userState = $(this).data("user-state");
          var action = "activate";
          if (userState === "on") {
              action = "deactivate";
          }
          $.ajax({
              url: `/${action}/${userId}`,
              type: "POST",
              success: function() {
                  window.location.href = "/admin_dashboard";
              }
          });
      });


4. **$(".column-order-btn").click: EventListener**::  
   Updates the page URL with new parameters for table ordering based on the selected column and rows per page.  
   The page is refreshed with the updated parameters.

   .. code-block:: javascript

      /**
       * Updates the page URL with new parameters for table ordering based on the selected column and rows per page.
       * The page is refreshed with the updated parameters.
       * 
       * @event
       * @param {Event} event - The click event triggered on the column-order-btn.
       */
      $(".column-order-btn").click(function() {
          var page = "{{ page }}";
          var rows_per_page = $(this).val();
          var column = $(this).data("column");
          window.location.href = get_url_for_table_order(page, rows_per_page, column);
      });


5. **$("#rows-per-page").change: EventListener**::  
   Updates the page URL with new parameters for rows per page and reloads the page with the updated parameters.

   .. code-block:: javascript

      /**
       * Updates the page URL with new parameters for rows per page and reloads the page with the updated parameters.
       * 
       * @event
       * @param {Event} event - The change event triggered on the rows-per-page input field.
       */
      $("#rows-per-page").change(function() {
          var rows_per_page = $(this).val();
          var urlParams = getAllUrlParams(window.location.href);
          var new_path = `{{ url_for('admin.admin_dashboard') }}?page=${1}&rows_per_page=${rows_per_page}`;
          
          if (urlParams.column !== undefined) {
              new_path += `&column=${urlParams.column}`;
          }
          if (urlParams.order !== undefined) {
              new_path += `&order=${urlParams.order}`;
          }
          window.location.href = new_path;
      });


6. **$(".page-btn").click: EventListener**::  
   Updates the page URL with the selected page number and reloads the page with the updated parameters.

   .. code-block:: javascript

      /**
       * Updates the page URL with the selected page number and reloads the page with the updated parameters.
       * 
       * @event
       * @param {Event} event - The click event triggered on the page-btn.
       */
      $(".page-btn").click(function() {
          var page = $(this).data("page");
          var urlParams = getAllUrlParams(window.location.href);
          var new_path = `{{ url_for('admin.admin_dashboard') }}?page=${page}&rows_per_page=${urlParams.rows_per_page}`;
          
          if (urlParams.column !== undefined) {
              new_path += `&column=${urlParams.column}`;
          }
          if (urlParams.order !== undefined) {
              new_path += `&order=${urlParams.order}`;
          }
          window.location.href = new_path;
      });


7. **get_url_for_table_order: Function**::  
   Generates the URL for table ordering based on the page number, rows per page, and column.  
   If the new URL is the same as the current path, it appends `&order=DESC`.

   .. code-block:: javascript

      /**
       * Generates the URL for table ordering based on the page number, rows per page, and column.
       * If the new URL is the same as the current path, it appends "&order=DESC".
       * 
       * @param {number} page - The current page number.
       * @param {number} rows_per_page - The number of rows per page.
       * @param {string} column - The column by which the table is ordered.
       * @returns {string} The new URL for table ordering.
       */
      function get_url_for_table_order(page, rows_per_page, column) {
          var new_path = `{{ url_for('admin.admin_dashboard') }}?page=${page}&rows_per_page=${rows_per_page}&column=${column}`;
          var current_path = window.location.pathname + window.location.search;
          
          if (new_path === current_path) {
              new_path += "&order=DESC";
          }
          return new_path;
      }


8. **getAllUrlParams: Function**::  
   Extracts and returns all URL parameters as an object, including handling array-like parameters.

   .. code-block:: javascript

      /**
       * Extracts and returns all URL parameters as an object.
       * Handles array-like parameters in the URL query string.
       * 
       * @param {string} url - The URL from which to extract parameters.
       * @returns {Object} An object containing the URL parameters as key-value pairs.
       */
      function getAllUrlParams(url) {
          var queryString = url ? url.split('?')[1] : window.location.search.slice(1);
          var obj = {};
          
          if (queryString) {
            queryString = queryString.split('#')[0];
            var arr = queryString.split('&');
    
            for (var i = 0; i < arr.length; i++) {
              var a = arr[i].split('=');
              var paramName = a[0];
              var paramValue = typeof (a[1]) === 'undefined' ? true : a[1];
              paramName = paramName.toLowerCase();
              
              if (typeof paramValue === 'string') paramValue = paramValue.toLowerCase();
              if (paramName.match(/\[(\d+)?\]$/)) {
                var key = paramName.replace(/\[(\d+)?\]/, '');
                
                if (!obj[key]) obj[key] = [];
                if (paramName.match(/\[\d+\]$/)) {
                  var index = /\[(\d+)\]/.exec(paramName)[1];
                  obj[key][index] = paramValue;
                } else {
                  obj[key].push(paramValue);
                }
              } else {
                if (!obj[paramName]) {
                  obj[paramName] = paramValue;
                } else if (obj[paramName] && typeof obj[paramName] === 'string'){
                  obj[paramName] = [obj[paramName]];
                  obj[paramName].push(paramValue);
                } else {
                  obj[paramName].push(paramValue);
                }
              }
            }
          }
          return obj;
      }
