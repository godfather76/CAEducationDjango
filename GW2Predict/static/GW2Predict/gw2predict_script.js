document.addEventListener("DOMContentLoaded", function() {
  const searchInput = document.getElementById("searchDropdown");
  const dropdownMenu = document.getElementById("dropdownMenu");
  const dropdownItems = document.querySelectorAll("#dropdownMenu li");

  // 1. FILTERING LOGIC
  searchInput.addEventListener("input", function() {
    const filterText = searchInput.value.toLowerCase();

    dropdownItems.forEach(function(item) {
      const buttonText = item.textContent.toLowerCase();
      if (buttonText.includes(filterText)) {
        item.style.display = "";
      } else {
        item.style.display = "none";
      }
    });
  });

  // 2. AUTOCOMPLETE ON CLICK LOGIC
  dropdownMenu.addEventListener("click", function(event) {
    // Check if the exact thing clicked was one of the dropdown buttons
    if (event.target.classList.contains("dropdown-item")) {

      // Grab the value from the data-value attribute (or textContent)
      const selectedValue = event.target.getAttribute("data-value");

      // Set the input field's value to the selected item
      searchInput.value = selectedValue;

      // Optional: Reset the list so all items show again next time you open it
      dropdownItems.forEach(function(item) {
        item.style.display = "";
      });
    }
  });

  // Prevent the dropdown from closing when clicking inside the input box to type
  searchInput.addEventListener("click", function(event) {
    event.stopPropagation();
  });

  const predict_button = document.getElementById("predict-button");
  const item = document.getElementById("searchDropdown");
  const predict_text = document.getElementById("predict-text");
  const baseUrl = '/GW2Predict/api/predict/'


  function predict() {
      const sel_item = item.value;
      const apiUrl = `${baseUrl}?item_name=${sel_item}`;
      if (sel_item.length < 1) {
          predict_text.textContent = 'You need to enter an item.';
      }else if (!dropdownMenu.querySelector(`[data-value="${sel_item}"]`)) {
          predict_text.textContent = 'That is not one of the items in the dropdown.';
      } else {
          // 1. Create the Abort Controller (the timeout watch)
            const controller = new AbortController();

            // 2. Set a timeout for 15 seconds (15000 milliseconds)
            const timeoutId = setTimeout(() => {
                controller.abort();
                console.warn("Request timed out! Forcing abort...");
            }, 15000);
            predict_text.textContent = 'Running prediction on ' + sel_item + '. Please wait...'
            fetch(apiUrl, {signal: controller.signal})
                .then(response => {
                    clearTimeout(timeoutId); // We were successful, end the timeout watch
                    if (!response.ok) throw new Error('Network response was not ok.');
                    return response.json();
                })
                .then(data => {
                    const features = data.features;
                    predict_text.innerHTML = features['item_name'] + ' (ID# ' + features['item_id'] + ')<br>' +
                    'Current Buy Price: ' + features['current_buy_price'] + '<br>' +
                    'Date of Feature Data: ' + features['data_date'] + '<br>' +
                    'Buy Open: ' +  features['buy_open'] + '&emsp;&emsp;' + 'Sell Open: ' + features['sell_open'] + '<br>' +
                    'Buy Low: ' + features['buy_low'] + '&emsp;&emsp;' + 'Sell Low: ' + features['sell_low'] + '<br>' +
                    'Buy High: ' + features['buy_high'] + '&emsp;&emsp;' + 'Sell High: ' + features['sell_high'] + '<br>' +
                    'Buy Close: ' + features['buy_close'] + '&emsp;&emsp;' + 'Sell Close: ' + features['sell_close'] + '<br>' +
                    'Buy SMA: ' + features['buy_sma'] + '&emsp;&emsp;' + 'Sell SMA: ' + features['sell_sma'] + '<br>' +
                    '3 day predicted price (' + features['3_day_date'] + '): ' + features['3d'] + '<br>' +
                    '7 day predicted price (' + features['7_day_date'] + '): ' + features['7d'] + '<br>' +
                    '30 day predicted price (' + features['30_day_date'] + '): ' + features['30d'];
                })
      }
  }
    predict_button.addEventListener("click", predict);

});