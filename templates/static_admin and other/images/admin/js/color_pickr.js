// Include jQuery
var script = document.createElement('script');
script.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

// Wait for jQuery to load before running our code
script.onload = function() {
    (function($) {
        $(document).ready(function() {
            function initColorPicker() {
                $('.color-picker').each(function() {
                    var $colorPicker = $(this);
                    var $row = $colorPicker.closest('tr');
                    var $redInput = $row.find('input[name$="-red"]');
                    var $greenInput = $row.find('input[name$="-green"]');
                    var $blueInput = $row.find('input[name$="-blue"]');

                    function updateColorPicker() {
                        var red = parseInt($redInput.val()).toString(16).padStart(2, '0');
                        var green = parseInt($greenInput.val()).toString(16).padStart(2, '0');
                        var blue = parseInt($blueInput.val()).toString(16).padStart(2, '0');
                        $colorPicker.val('#' + red + green + blue);
                    }

                    function updateRGBInputs() {
                        var color = $colorPicker.val().substring(1); // Remove the #
                        var rgb = parseInt(color, 16);
                        $redInput.val((rgb >> 16) & 0xff);
                        $greenInput.val((rgb >> 8) & 0xff);
                        $blueInput.val(rgb & 0xff);
                    }

                    $colorPicker.on('input', updateRGBInputs);
                    $redInput.add($greenInput).add($blueInput).on('input', updateColorPicker);

                    // Initial update
                    updateColorPicker();
                });
            }

            // Initialize on page load
            initColorPicker();

            // Re-initialize when a new inline form is added
            $(document).on('formset:added', function(event, $row, formsetName) {
                initColorPicker();
            });
        });
    })(jQuery);
};