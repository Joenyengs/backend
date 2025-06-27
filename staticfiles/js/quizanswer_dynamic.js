(function($) {
    $(function() {
        var $question = $('#id_question');
        var $selectedOption = $('#id_selected_option');

        function updateOptions(questionId) {
            if (!questionId) return;
            $.ajax({
                url: '/api/recrutement/admin/get-question-options/' + questionId + '/',
                method: 'GET',
                success: function(data) {
                    $selectedOption.empty();
                    $.each(data, function(key, value) {
                        $selectedOption.append(
                            $('<option></option>').attr('value', key).text(value)
                        );
                    });
                }
            });
        }

        $question.change(function() {
            var questionId = $(this).val();
            updateOptions(questionId);
        });

        // Si une question est déjà sélectionnée au chargement
        if ($question.val()) {
            updateOptions($question.val());
        }
    });
})(django.jQuery);