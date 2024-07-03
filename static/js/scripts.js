function toggleSelectAll(source) {
    let checkboxes = source.closest('table').querySelectorAll('input[type="checkbox"]');
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i] !== source) {
            checkboxes[i].checked = source.checked;
        }
    }
    updateSelectedCounts(source.closest('.content').previousElementSibling.textContent.trim());
}

function selectRandomQuestions(section) {
    let numQuestions = document.getElementById('num_questions_' + section).value;
    let checkboxes = document.querySelectorAll('.content input[type="checkbox"][name="question"][value^="' + section + '-"]');
    let checkboxesArray = Array.from(checkboxes);

    // Clear all checkboxes first
    checkboxesArray.forEach(function (checkbox) {
        checkbox.checked = false;
    });

    // Shuffle array
    for (let i = checkboxesArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [checkboxesArray[i], checkboxesArray[j]] = [checkboxesArray[j], checkboxesArray[i]];
    }

    // Select the required number of questions
    for (let i = 0; i < numQuestions && i < checkboxesArray.length; i++) {
        checkboxesArray[i].checked = true;
    }

    updateSelectedCounts(section);
}

function updateQuestionCounts() {
    let sections = document.getElementsByClassName('collapsible');
    for (let i = 0; i < sections.length; i++) {
        let section = sections[i].textContent.trim();
        let checkboxes = document.querySelectorAll('.content input[type="checkbox"][name="question"][value^="' + section + '-"]');
        let easyCounts = 0, moderateCounts = 0, difficultCounts = 0;

        checkboxes.forEach(function (checkbox) {
            switch (checkbox.getAttribute('data-difficulty').toLowerCase()) {
                case 'easy':
                    easyCounts++;
                    break;
                case 'moderate':
                    moderateCounts++;
                    break;
                case 'difficult':
                    difficultCounts++;
                    break;
            }
        });

        document.getElementById(section + '-easy-count').textContent = easyCounts;
        document.getElementById(section + '-moderate-count').textContent = moderateCounts;
        document.getElementById(section + '-difficult-count').textContent = difficultCounts;
    }
}

function updateSelectedCounts(section) {
    let checkboxes = document.querySelectorAll('.content input[type="checkbox"][name="question"][value^="' + section + '-"]');
    let easySelected = 0, moderateSelected = 0, difficultSelected = 0;

    checkboxes.forEach(function (checkbox) {
        if (checkbox.checked) {
            switch (checkbox.getAttribute('data-difficulty').toLowerCase()) {
                case 'easy':
                    easySelected++;
                    break;
                case 'moderate':
                    moderateSelected++;
                    break;
                case 'difficult':
                    difficultSelected++;
                    break;
            }
        }
    });

    document.getElementById(section + '-easy-selected').textContent = easySelected;
    document.getElementById(section + '-moderate-selected').textContent = moderateSelected;
    document.getElementById(section + '-difficult-selected').textContent = difficultSelected;
}

let coll = document.getElementsByClassName("collapsible");
for (let i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function () {
        this.classList.toggle("active");
        let content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
            updateQuestionCounts(); // Update counts when section is opened
            updateSelectedCounts(this.textContent.trim());
        }
    });
}

// Call updateQuestionCounts when the page loads
window.onload = function () {
    updateQuestionCounts();
    let sections = document.getElementsByClassName('collapsible');
    for (let i = 0; i < sections.length; i++) {
        updateSelectedCounts(sections[i].textContent.trim());
    }
};
