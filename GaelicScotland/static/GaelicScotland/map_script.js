document.addEventListener("DOMContentLoaded", function() {
    function checkLeaflet() {
        if (window.leafletLoaded || (typeof L !== 'undefined')) {
            console.log("Leaflet library ready, initializing map...");
            initializeMyMap();
        } else {
            console.log("Waiting for Leaflet...");
            setTimeout(checkLeaflet, 200);
        }
    }

    checkLeaflet();

    function initializeMyMap() {
        // Scottish geographic bounds
        var scotlandBounds = L.latLngBounds(
            L.latLng(54.6, -8.6), // Southwest corner
            L.latLng(60.9, -0.7)  // Northeast corner
        );

        // 1. Initialize map centered on Scotland
        var map = L.map('map', {
            maxBounds: scotlandBounds,
            maxBoundsViscosity: 1.0,
            minZoom: 6
        }).setView([56.4907, -4.2026], 7);

        setTimeout(function () {
            map.invalidateSize();
        }, 100);

        // 2. Load geographic underlying base tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);
        /* Helper to scale raw counts to pixel radius (adjust scale multiplier as needed)
        function getBubbleRadius(val) {
            if (!val || val <= 0) return 0;
            // Square root scaling prevents high numbers from blowing out the map
            return Math.sqrt(val) * 0.8;
        }
        */

        var geojsonLayer;
        // var bubbleLayer;

        function getSpeakersColor(speakers) {
            if (speakers === null || speakers === undefined) return '#e0e0e0'; // Make missing data gray
            return speakers > 9 ? '#04234b' : // Deepest Navy
                speakers > 8 ? '#0a3a69' : // Dark Navy Blue
                    speakers > 7 ? '#145082' : // Dark Blue
                        speakers > 6 ? '#22659b' : // Strong Blue
                            speakers > 5 ? '#317bb4' : // Medium Dark Blue
                                speakers > 4 ? '#478ebf' : // Medium Blue
                                    speakers > 3 ? '#63a0ca' : // Muted Blue
                                        speakers > 2 ? '#7eb1d4' : // Soft Blue
                                            speakers > 1 ? '#9ac3df' : // Light Blue
                                                '#b5d4e9';  // Pale Blue (Distinctly blue, not white)
        }

        // 3. Consolidated operational data loading container block
        function loadConstituencyData(retries = 3) {
            var apiUrl = '/GaelicScotland/api/scottish-constituencies/';

            const controller = new AbortController();
            const timeoutId = setTimeout(() => {
                controller.abort();
                console.warn("Request timed out! Forcing abort...");
            }, 15000);

            fetch(apiUrl, {signal: controller.signal})
                .then(response => {
                    clearTimeout(timeoutId);
                    if (!response.ok) throw new Error('Network response not ok');
                    return response.json();
                })
                .then(data => {
                    if (geojsonLayer) {
                        map.removeLayer(geojsonLayer);
                    }

                    /*
                    if (bubbleLayer) {
                        map.removeLayer(bubbleLayer);
                    }
                    */

                    // 4. Draw our spatial layout features
                    geojsonLayer = L.geoJSON(data, {
                        style: function (feature) {
                            var speakers = feature.properties.perc_some_gaelic;
                            if (speakers === null || speakers === undefined || speakers === '' || isNaN(speakers)) {
                                return {
                                    color: '#fffff',
                                    fillColor: '#e0e0e0',
                                    weight: 1.5,
                                    fillOpacity: 0.75
                                }
                            }

                            return {
                                color: "#fffff", // Subtle aesthetic variance for clarity
                                fillColor: getSpeakersColor(speakers),
                                weight: 1.5,
                                fillOpacity: 0.8
                            };
                        },
                        onEachFeature: function (feature, layer) {
                            layer.on({
                                mouseover: function (e) {
                                    var polygon = e.target;

                                    polygon.setStyle({
                                        weight: 3,
                                        color: '#666',
                                        fillOpacity: 0.8
                                    });

                                    var props = feature.properties;
                                    var constituency = props.constituency || props.constituency || "Unknown Constituency";
                                    var tooltipContent = "<strong>" + constituency + "</strong><br>";

                                    tooltipContent += 'Population Over 3: ' + props.pop_over_3 + '<br>';
                                    tooltipContent += 'No Gaelic: ' + props.num_no_gaelic + ' (' + props.perc_no_gaelic + '%)<br>';
                                    tooltipContent += 'Some Gaelic: ' + props.num_some_gaelic + ' (' + props.perc_some_gaelic + '%)<br><br>';
                                    tooltipContent += 'Trans or Trans History: ' + props.num_trans + ' (' + props.perc_trans + '%)<br>';
                                    tooltipContent += 'Not Trans and no Trans History: ' + props.num_not_trans + ' (' + props.perc_not_trans + '%)<br>';
                                    tooltipContent += 'No answer: ' + props.num_not_answered + ' (' + props.perc_not_answered + '%)<br>';


                                    polygon.bindTooltip(tooltipContent, {sticky: true, direction: 'auto'}).openTooltip();
                                },

                                mouseout: function (e) {
                                    geojsonLayer.resetStyle(e.target);
                                    e.target.closeTooltip();
                                }
                            });
                        }
                    }).addTo(map);

                    /*
                    bubbleLayer = L.layerGroup().addTo(map);

                    data.features.forEach(function(feature) {
                        var props = feature.properties;
                        var transCount = props.num_trans;
                        var radius = getBubbleRadius(transCount);

                        // Read pre-calculated centroid [lng, lat] -> Leaflet uses [lat, lng]
                        if (radius > 0 && props.centroid) {
                            var latLng = [props.centroid[1], props.centroid[0]];

                            var bubble = L.circleMarker(latLng, {
                                radius: radius,
                                fillColor: "#ff5500",
                                color: "#ffffff",
                                weight: 1.5,
                                opacity: 1.0,
                                fillOpacity: 0.65
                            });

                            var tooltipContent = "<strong>" + props.constituency + "</strong><br>" +
                                "Population over 16: " + props.pop_over_16.toLocaleString() + "<br>" +
                                "Trans or Trans History: " + props.num_trans.toLocaleString() + " (" + props.perc_trans + "%)<br>" +
                                "Not Trans: " + props.num_not_trans.toLocaleString() + " (" + props.perc_not_trans + "%)<br>" +
                                "No answer: " + props.num_not_answered.toLocaleString() + " (" + props.perc_not_answered + "%)";

                            bubble.bindTooltip(tooltipContent, {sticky: true, direction: 'auto'});

                            bubble.on('mouseover', function (e) {
                                e.target.setStyle({fillOpacity: 0.9, weight: 3});
                            });
                            bubble.on('mouseout', function (e) {
                                e.target.setStyle({fillOpacity: 0.65, weight: 1.5});
                            });

                            bubble.addTo(bubbleLayer);
                        }
                    });
                    */
                })
                .catch(error => {
                    clearTimeout(timeoutId);

                    if (error.name === 'AbortError') {
                        console.error('Fetch aborted due to server timeout.');
                    } else {
                        console.error('Error loading data:', error);
                    }

                    if (retries > 0) {
                        console.warn(`Retrying in 2s... (${retries} attempts left)`);
                        setTimeout(() => loadConstituencyData(retries - 1), 2000);
                    } else {
                        console.error('Final attempt failed. Please refresh the page.');
                    }
                });
        }

        var legend = L.control({position: 'topright'});

        legend.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'info legend');

            // 1. Label for the base choropleth map
            div.innerHTML += '<strong style="display:block; margin-bottom:6px;">Gaelic Speakers</strong>';

            var grades = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

            // Loop through intervals and generate a label with a colored square for each
            for (var i = 0; i < grades.length; i++) {
                var from = grades[i];
                var to = grades[i + 1];

                // Call the updated getSpeakersColor function
                div.innerHTML +=
                    '<i style="background:' + getSpeakersColor(from + 1) + '"></i> ' +
                    from + (to ? '&ndash;' + to + '%' : '+%') + '<br>';
            }

            /* 2. Label and visual key for the proportional bubbles overlay
            div.innerHTML += '<hr style="margin: 10px 0; border: 0; border-top: 1px solid #ccc;">';
            div.innerHTML += '<strong style="display:block; margin-bottom:6px;">Trans Population</strong>';

            // Use spans with inline CSS to draw circles that bypass standard Leaflet legend square styling
            div.innerHTML +=
                '<div style="margin-bottom: 4px; display: flex; align-items: center;">' +
                '<span style="background: #ff5500; border: 1px solid #ffffff; width: 10px; height: 10px; border-radius: 50%; opacity: 0.65; display: inline-block; margin-right: 12px; margin-left: 4px;"></span> Lower' +
                '</div>' +
                '<div style="display: flex; align-items: center;">' +
                '<span style="background: #ff5500; border: 1px solid #ffffff; width: 16px; height: 16px; border-radius: 50%; opacity: 0.65; display: inline-block; margin-right: 9px; margin-left: 1px;"></span> Higher' +
                '</div>';
            */

            return div;
        };
        legend.addTo(map);
        loadConstituencyData();
    }
});