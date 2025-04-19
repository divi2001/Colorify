(function($) {
    $(document).ready(function() {
        var numColorsField = $('#id_num_colors');
        var colorInlineFormset = $('.inline-group');
        var emptyForm = $('.empty-form').clone().removeClass('empty-form');
        var totalFormsInput = $('#id_colors-TOTAL_FORMS');

        function updateColorForms() {
            var numColors = parseInt(numColorsField.val());
            var currentForms = colorInlineFormset.find('.dynamic-colors').length;

            if (numColors > currentForms) {
                // Add new color forms
                for (var i = currentForms; i < numColors; i++) {
                    var newForm = emptyForm.clone(true);
                    newForm.removeClass('empty-form').addClass('dynamic-colors');
                    newForm.find('h3').text('Color #' + (i + 1));
                    newForm.find(':input').each(function() {
                        var name = $(this).attr('name').replace('__prefix__', i);
                        var id = 'id_' + name;
                        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
                    });
                    colorInlineFormset.append(newForm);
                }
            } else if (numColors < currentForms) {
                // Remove excess color forms
                colorInlineFormset.find('.dynamic-colors').slice(numColors).remove();
            }

            // Update the management form
            totalFormsInput.val(numColors);

            // Renumber the forms
            colorInlineFormset.find('.dynamic-colors').each(function(index) {
                $(this).find('h3').text('Color #' + (index + 1));
            });
        }

        numColorsField.on('change', updateColorForms);

        // Initial setup
        updateColorForms();
    });
})(django.jQuery);
(function($) {
    $(document).ready(function() {
        const baseColorPicker = $('input.color-picker');
        const autoGenerateCheckbox = $('input.auto-generate-checkbox');
        const numColorsInput = $('#id_num_colors');
        const typeSelect = $('#id_type');

        function updateColors() {
            if (!autoGenerateCheckbox.is(':checked')) return;

            const baseColor = baseColorPicker.val();
            const numColors = numColorsInput.val();
            const paletteType = typeSelect.val();

            // Get the palette ID if we're editing an existing palette
            const paletteId = window.location.pathname.split('/')[4];

            $.ajax({
                url: `/admin/yourapp/palette/${paletteId}/update_colors/`,
                method: 'POST',
                data: {
                    base_color: baseColor,
                    num_colors: numColors,
                    type: paletteType,
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    if (response.status === 'success') {
                        location.reload();
                    }
                }
            });
        }

        // Update colors when base color, number of colors, or type changes
        baseColorPicker.on('change', updateColors);
        numColorsInput.on('change', updateColors);
        typeSelect.on('change', updateColors);

        // Show/hide color inputs based on auto-generate checkbox
        autoGenerateCheckbox.on('change', function() {
            const colorInputs = $('.rgb-input');
            if ($(this).is(':checked')) {
                colorInputs.prop('readonly', true);
            } else {
                colorInputs.prop('readonly', false);
            }
        });
    });
})(django.jQuery);