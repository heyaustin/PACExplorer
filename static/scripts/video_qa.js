
function sendSelection(optionIndex, button) {

    var buttons = document.querySelectorAll('button');
    buttons.forEach(function (button) {
        button.disabled = false;
    });

    button.disabled = true;

    choose[questionNumber] = optionIndex;
    var questionDiv = document.getElementById('question' + (questionNumber + 1));
    questionDiv.textContent = '第' + (questionNumber + 1) + '題： ' + (optionIndex + 1);
    //計算是否是最後一個按鈕
    if (!isAllSelect) {
        isAllSelect = true;
        for (var i = 0; i < totalQuestionNumber; i++) {
            if (choose[i] == -1) {
                isAllSelect = false;
                break;
            }
        }
        if (isAllSelect) document.getElementById("send").hidden = false;
    }

    fetch('/save_selection/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN,
            // https://stackoverflow.com/questions/43255819/why-do-i-get-a-csrf-token-missing-or-incorrect-error
            // the HEADER key should be X-CSRFToken as for Django 2.1, links goes here https://docs.djangoproject.com/en/2.1/ref/csrf/
        },
        credentials: "same-origin",
        body: JSON.stringify({ selectedOption: optionIndex, questionNumber: questionNumber })
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
}


function checkAnswers() {
    let allAnswered = true;

    if (typeof choose === 'string' || choose instanceof String) {
        choose = JSON.parse(choose)
    }

    for (let i = 0; i < choose.length; i++) {
        if (choose[i] === -1) {
            allAnswered = false;
            Swal.fire({
                title: "第" + String(i + 1) + "題未作答",
                icon: "error",
                imageHeight: 156,
                imageWidth: 173,
                imageAlt: "A tall image",
                confirmButtonText: '<img src="/static/images/send_success.png" alt="Confirm">',
                confirmButtonColor: 'transparent',
                customClass: {
                    confirmButton: 'confirm_button'
                }
            });
            break;
        }
    }

    if (allAnswered) {
        Swal.fire({
            title: "送出成功",
            imageUrl: "/static/images/check.png",
            imageHeight: 156,
            imageWidth: 173,
            imageAlt: "A tall image",
            confirmButtonText: '<img src="/static/images/send_success.png" alt="Confirm">',
            confirmButtonColor: 'transparent',
            customClass: {
                confirmButton: 'confirm_button'
            }
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = '/video_result';
            }
        });
    }
}
