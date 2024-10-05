
function selectOption(questionId, optionIndex) {
    fetch('/save_selection/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            questionId: questionId,
            selectedOption: optionIndex
        })
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
}

function validateForm() {
    var questions = document.querySelectorAll('.question');
    var allQuestionsAnswered = true;

    for (const question of questions) {
        var options = [];
        var currentElement = question.nextElementSibling;
        while (currentElement && options.length < 4) {
            if (currentElement.querySelector('input[type="radio"]')) {
                options.push(currentElement.querySelector('input[type="radio"]'));
            }
            currentElement = currentElement.nextElementSibling;
        }

        var optionsChecked = options.some(radio => radio.checked);

        if (!optionsChecked) {
            Swal.fire({
                title: "請回答所有問題",
                icon: "error"
            });
            allQuestionsAnswered = false;
            break;
        }
    }

    return allQuestionsAnswered;
}
