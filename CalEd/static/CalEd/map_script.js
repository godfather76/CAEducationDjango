document.addEventListener("DOMContentLoaded", function() {
    function checkLeaflet() {
        if (window.leafletLoaded || (typeof L !== 'undefined')) {
            console.log("Leaflet library ready, initializing map...");
            // --- ALL YOUR EXISTING CODE STARTING FROM 'var caBounds = ...' ---
            // ...
        } else {
            console.log("Waiting for Leaflet...");
            setTimeout(checkLeaflet, 200); // Poll every 200ms
        }
    }
    checkLeaflet();
    var caBounds = L.latLngBounds(
    L.latLng(32.5, -124.5), // Southwest corner
    L.latLng(42.0, -114.1)  // Northeast corner
    );
    // 1. Initialize your map canvas (centered on California)
    var map = L.map('map', {
        maxBounds: caBounds,
        maxBoundsViscosity: 1.0 // Prevents the user from dragging outside the bounds at all
    }).setView([36.7783, -119.4179], 6);

    // Force Leaflet to recognize the div size immediately
    setTimeout(function(){
        map.invalidateSize();
    }, 100);

    // 2. Load geographic underlying base tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    // Bind references to DOM control elements
    var boundaryDropdown = document.getElementById('boundary-dropdown')
    var yearDropdown = document.getElementById('year-dropdown');
    var staffDropdown = document.getElementById('staff-dropdown');
    var payDropdown = document.getElementById('pay-dropdown');
    var testDropdown = document.getElementById('test-dropdown')
    var studentGroupDropdown = document.getElementById('studentgroup-dropdown')
    var scoreDropdown = document.getElementById('score-dropdown')

    // -----------------------------------------------------------------
    // NOTATION: DECLARE FUTURE DROPDOWN DOM VARIABLES HERE
    // var customDropdown = document.getElementById('custom-dropdown');
    // -----------------------------------------------------------------

    var currentMetric = payDropdown ? payDropdown.value : 'total_pay_and_benefits';

    if (payDropdown) {
        payDropdown.addEventListener('change', function (e) {
            currentMetric = e.target.value; // Updates client text instantly on hover without API lag
            console.log("Metric changed to:", currentMetric)
        });
    }

    // Retain a dynamic reference handle to clear layer assets before redraw cycles
    var geojsonLayer;

    // Create a color helper function to sort by score
    function getScoreColorPercent(score) {
        if (score === null || score === undefined) return '#e0e0e0'; // Make missing data gray

        return score > 90 ? '#02e302' : // Pure Vibrant Green
       score > 80 ? '#60e302' : // Light Lime Green
       score > 70 ? '#f2f202' : // Pure Vibrant Yellow
       score > 60 ? '#f2ca02' : // Golden Yellow
       score > 50 ? '#e39b02' : // Amber / Yellow-Orange
       score > 40 ? '#e37a02' : // Vibrant Orange
       score > 30 ? '#e35802' : // Deep Orange
       score > 20 ? '#e33602' : // Red-Orange
       score > 10 ? '#e31802' : // Bright Red
                    '#e30202';  // Deep Crimson Red

        // Scale that makes anything less than 50% red
        // return score > 90 ? '#0af613' : // Dark Green (Excellent)
        //    score > 80 ? '#c2f606' : // Light Green
        //    score > 70 ? '#fbc103' : // Yellow-Green
        //    score > 60 ? '#ff9100f9' : // Orange/Yellow
        //    score > 50 ? '#fd5a03' : // Dark Orange
        //                 '#fd0420cc'; // Red (Needs Improvement)
    }


    // 3. Consolidated operational data loading container block
    function loadDistrictData(retries = 3) {
        var boundaryType = boundaryDropdown ? boundaryDropdown.value : 'district';
        var year = yearDropdown ? yearDropdown.value : '2022';
        var staffType = staffDropdown ? staffDropdown.value : 'TA';
        var test = testDropdown ? testDropdown.value : 'SB - English Language Arts/Literacy'
        var student_group = studentGroupDropdown ? studentGroupDropdown.value : 'All Students'
        var score_type = scoreDropdown ? scoreDropdown.value : 'Percentage Met and Above'

        var baseUrl = (boundaryType === 'county') ? '/api/counties/' : '/api/districts/';
        var apiUrl = `${baseUrl}?staff_type=${staffType}&year=${year}&test=${test}&student_group=${student_group}&score=${score_type}`;

        console.log("Fetching data, attempts remaining:", retries);

        // 1. Create the Abort Controller (The Stopwatch)
        const controller = new AbortController();

        // 2. Set a timeout for 15 seconds (15000 milliseconds)
        const timeoutId = setTimeout(() => {
            controller.abort();
            console.warn("Request timed out! Forcing abort...");
        }, 15000);

        fetch(apiUrl)
            .then(response => {
                clearTimeout(timeoutId); // Success! Stop the stopwatch.
                if (!response.ok) throw new Error('Network response not ok');
                return response.json();
            })
            .then(data => {
                console.log("Data received. Features count:", data.features.length);
                // Clean active layers off the map structure to block memory leaks
                if (geojsonLayer) {
                    map.removeLayer(geojsonLayer);
                }

                // 4. Draw our spatial layout features
                geojsonLayer = L.geoJSON(data, {
                    style: function (feature) {
                        if (score_type === 'Percentage Met and Above') {
                            var score = feature.properties.percentage_met_above;
                        } else if (score_type === 'Percentage Nearly Met') {
                            var score = feature.properties.percentage_nearly_met;
                        } else if (score_type === 'Percentage Nearly Met and Above') {
                            var score = feature.properties.percentage_nearly_met_above;
                        }



                        if (score === null || score === undefined || score === '' || isNaN(score)) {
                            return {
                                color: '#fffff',
                                fillColor: '#e0e0e0',
                                weight: 1.5,
                                fillOpacity: 0.4
                            }
                        }

                        return {
                            color: "#fffff", // Subtle aesthetic variance for clarity
                            fillColor: getScoreColorPercent(score),
                            weight: 1.5,
                            fillOpacity: 0.8
                        };
                    },
                    onEachFeature: function (feature, layer) {
                        layer.on({
                            mouseover: function (e) {
                                var polygon = e.target;

                                // Visual highlighting feedback trace
                                polygon.setStyle({
                                    weight: 3,
                                    color: '#666',
                                    fillOpacity: 0.5
                                });

                                var props = feature.properties;
                                var name = props.district || props.county || "Unknown Regional entity";
                                var labelSuffix = (boundaryType === 'county') ? " County" : " School District";
                                var tooltipContent = "<strong>" + name + labelSuffix + "</strong><br>";
                                if (score_type === 'Percentage Met and Above') {
                                    var score = feature.properties.percentage_met_above;
                                } else if (score_type === 'Percentage Nearly Met') {
                                    var score = feature.properties.percentage_nearly_met;
                                } else if (score_type === 'Percentage Nearly Met and Above') {
                                    var score = feature.properties.percentage_nearly_met_above;
                                }

                                // Check active UI choice selection variable to adjust tooltip markup layout string
                                if (currentMetric === 'regular_pay') {
                                    var regular_pay_mean = props.regular_pay_mean ? props.regular_pay_mean.toLocaleString() : 'Data Unavailable';
                                    var regular_pay_min = props.regular_pay_min ? props.regular_pay_min.toLocaleString() : 'Data Unavailable';
                                    var regular_pay_max = props.regular_pay_max ? props.regular_pay_max.toLocaleString() : 'Data Unavailable';
                                    var regular_pay_sum = props.regular_pay_sum ? props.regular_pay_sum.toLocaleString() : 'Data Unavailable';
                                    tooltipContent += "Mean Regular Pay:    $" + regular_pay_mean + "<br>";
                                    tooltipContent += "Minimum Regular Pay: $" + regular_pay_min + "<br>";
                                    tooltipContent += "Maximum Regular Pay: $" + regular_pay_max;
                                } else if (currentMetric === 'overtime_pay') {
                                    var overtime_pay_mean = props.overtime_pay_mean ? props.overtime_pay_mean.toLocaleString() : 'Data Unavailable';
                                    var overtime_pay_min = props.overtime_pay_min ? props.overtime_pay_min.toLocaleString() : 'Data Unavailable';
                                    var overtime_pay_max = props.overtime_pay_max ? props.overtime_pay_max.toLocaleString() : 'Data Unavailable';
                                    var overtime_pay_sum = props.overtime_pay_sum ? props.overtime_pay_sum.toLocaleString() : 'Data Unavailable';
                                    tooltipContent += "Mean Overtime Pay:    $" + overtime_pay_mean + "<br>";
                                    tooltipContent += "Minimum Overtime Pay: $" + overtime_pay_min + "<br>";
                                    tooltipContent += "Maximum Overtime Pay: $" + overtime_pay_max;
                                } else if (currentMetric === 'other_pay') {
                                    var other_pay_mean = props.other_pay_mean ? props.other_pay_mean.toLocaleString() : 'Data Unavailable';
                                    var other_pay_min = props.other_pay_min ? props.other_pay_min.toLocaleString() : 'Data Unavailable';
                                    var other_pay_max = props.other_pay_max ? props.other_pay_max.toLocaleString() : 'Data Unavailable';
                                    var other_pay_sum = props.other_pay_sum ? props.other_pay_sum.toLocaleString() : 'Data Unavailable';
                                    tooltipContent += "Mean Other Pay:    $" + other_pay_mean + "<br>";
                                    tooltipContent += "Minimum Other Pay: $" + other_pay_min + "<br>";
                                    tooltipContent += "Maximum Other Pay: $" + other_pay_max;
                                } else if (currentMetric === 'total_pay') {
                                    var total_pay_mean = props.total_pay_mean ? props.total_pay_mean.toLocaleString() : 'Data Unavailable';
                                    var total_pay_min = props.total_pay_min ? props.total_pay_min.toLocaleString() : 'Data Unavailable';
                                    var total_pay_max = props.total_pay_max ? props.total_pay_max.toLocaleString() : 'Data Unavailable';
                                    var total_pay_sum = props.total_pay_sum ? props.total_pay_sum.toLocaleString() : 'Data Unavailable';
                                    tooltipContent += "Mean Total Pay:    $" + total_pay_mean + "<br>";
                                    tooltipContent += "Minimum Total Pay: $" + total_pay_min + "<br>";
                                    tooltipContent += "Maximum Total Pay: $" + total_pay_max ;
                                } else if (currentMetric === 'benefits') {
                                    var benefits_mean = props.benefits_mean ? props.benefits_mean.toLocaleString() : 'Data Unavailable';
                                    var benefits_min = props.benefits_min ? props.benefits_min.toLocaleString() : 'Data Unavailable';
                                    var benefits_max = props.benefits_max ? props.benefits_max.toLocaleString() : 'Data Unavailable';
                                    var benefits_sum = props.benefits_sum ? props.benefits_sum.toLocaleString() : 'Data Unavailable';
                                    tooltipContent += "Mean Benefits:    $" + benefits_mean + "<br>";
                                    tooltipContent += "Minimum Benefits: $" + benefits_min + "<br>";
                                    tooltipContent += "Maximum Benefits: $" + benefits_max;
                                } else if (currentMetric === 'total_pay_and_benefits') {
                                    var total_pay_and_benefits_mean = props.total_pay_and_benefits_mean ? props.total_pay_and_benefits_mean.toLocaleString() : 'Data Unavailable';
                                    var total_pay_and_benefits_min = props.total_pay_and_benefits_min ? props.total_pay_and_benefits_min.toLocaleString() : 'Data Unavailable';
                                    var total_pay_and_benefits_max = props.total_pay_and_benefits_max ? props.total_pay_and_benefits_max.toLocaleString() : 'Data Unavailable';
                                    var total_pay_and_benefits_sum = props.total_pay_and_benefits_sum ? props.total_pay_and_benefits_sum.toLocaleString() : 'Data Unavailable';
                                    tooltipContent += "Mean Total Pay and Benefits:    $" + total_pay_and_benefits_mean + "<br>";
                                    tooltipContent += "Minimum Total Pay and Benefits: $" + total_pay_and_benefits_min + "<br>";
                                    tooltipContent += "Maximum Total Pay and Benefits: $" + total_pay_and_benefits_max;
                                }
                                tooltipContent += "<br><hr style='margin:5px 0;'>"; // Add a nice subtle separation line
                                tooltipContent += score_type + ": " + score;
                                if (score_type === 'Percentage Met and Above' || score_type === 'Percentage Nearly Met') {
                                    tooltipContent += "%";
                                }
                                tooltipContent += "<br>";
                                // -----------------------------------------------------------------
                                // NOTATION: EXTEND TOOLTIP TEXT FOR FUTURE DISPLAY METRICS HERE
                                // -----------------------------------------------------------------

                                // Anchor tooltip tightly to user pointer actions
                                polygon.bindTooltip(tooltipContent, {sticky: true, direction: 'auto'}).openTooltip();
                            },

                            mouseout: function (e) {
                                geojsonLayer.resetStyle(e.target);
                                e.target.closeTooltip();
                            }
                        });
                    }
                }).addTo(map);
            })
            .catch(error => {
                clearTimeout(timeoutId); // Stop the stopwatch on error too

            // Check if the error was caused by our timeout
            if (error.name === 'AbortError') {
                console.error('Fetch aborted due to server timeout.');
            } else {
                console.error('Error loading data:', error);
            }

            // Trigger the retry logic
            if (retries > 0) {
                console.warn(`Retrying in 2s... (${retries} attempts left)`);
                setTimeout(() => loadDistrictData(retries - 1), 2000);
            } else {
                console.error('Final attempt failed. Please refresh the page.');
            }
            });

    }

    // Attach operational listener arrays to refresh layer calculations when filters shift
    if (boundaryDropdown) boundaryDropdown.addEventListener('change', loadDistrictData)
    if (yearDropdown) yearDropdown.addEventListener('change', loadDistrictData);
    if (staffDropdown) staffDropdown.addEventListener('change', loadDistrictData);
    if (payDropdown) payDropdown.addEventListener('change', loadDistrictData)
    if (testDropdown) testDropdown.addEventListener('change', loadDistrictData)
    if (studentGroupDropdown) studentGroupDropdown.addEventListener('change', loadDistrictData)
    if (scoreDropdown) scoreDropdown.addEventListener('change', loadDistrictData)


    // -----------------------------------------------------------------
    // NOTATION: ATTACH CHANGE LISTENERS TO PROCESS FUTURE RE-FETCH DROPDOWNS HERE
    // if (customDropdown) customDropdown.addEventListener('change', loadDistrictData);
    // -----------------------------------------------------------------
    var legend = L.control({ position: 'topright' });

    legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend');
        // Define the lower boundaries of your score increments
        var grades = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90];

        div.innerHTML += '<strong>Score Scale</strong><br>';

        // Loop through intervals and generate a label with a colored square for each
        for (var i = 0; i < grades.length; i++) {
            var from = grades[i];
            var to = grades[i + 1];

            // Passing (from + 1) ensures it hits the correct conditional bracket in your function
            div.innerHTML +=
                '<i style="background:' + getScoreColorPercent(from + 1) + '"></i> ' +
                from + (to ? '&ndash;' + to + '%' : '+%') + '<br>';
        }

        return div;
    };

    legend.addTo(map);
    // Boot initialization runtime cycle on load execution footprint
    loadDistrictData();
});