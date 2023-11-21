import { data } from './data.js';

const codeSelect = document.getElementById('code');
const bookSelect = document.getElementById('book');
const titleSelect = document.getElementById('title');
const chapterSelect = document.getElementById('chapter');

function populateSelect(selectElement, options) {
    selectElement.innerHTML = ''; // Clear the select element

    // Create and add a default "Select an option" choice
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '';
    selectElement.appendChild(defaultOption);

    options.forEach((option) => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        selectElement.appendChild(optionElement);
    });
}


// Function to populate the next select based on the previous one
function populateNextSelect(previousSelect, nextSelect, columnIndex) {
    const selectedOption = previousSelect.value;

    const filteredData = data.filter((row) => row[columnIndex - 1] === selectedOption);

    const uniqueOptions = [...new Set(filteredData.map((row) => row[columnIndex]))];

    populateSelect(nextSelect, uniqueOptions);
}

codeSelect.addEventListener('change', () => {
    bookSelect.innerHTML = '';
    titleSelect.innerHTML = '';
    chapterSelect.innerHTML = '';
    populateNextSelect(codeSelect, bookSelect, 1);
});

bookSelect.addEventListener('change', () => {
    titleSelect.innerHTML = '';
    chapterSelect.innerHTML = '';
    populateNextSelect(bookSelect, titleSelect, 2);
});

titleSelect.addEventListener('change', () => {
    chapterSelect.innerHTML = '';
    populateNextSelect(titleSelect, chapterSelect, 3);
});

// Initialize the code select
populateSelect(codeSelect, [...new Set(data.map((row) => row[0]))]);

document.getElementById("code").addEventListener("change", function () {
    var codeSelect = document.getElementById("code");
    var bookLabel = document.querySelector("label[for='book']");

    if (codeSelect.value === "แพ่งและพาณิชย์") {
        bookLabel.textContent = "บรรพ";
    } else {
        bookLabel.textContent = "ภาค";
    }

});
function removeWordFromAllDivs() {
    // Get all elements with the class "card-header"
    var divs = document.querySelectorAll(".card-header");

    // Loop through each div
    divs.forEach(function (div) {
        var text = div.textContent;

        // Check if the text contains "พ.ร.บ"
        if (text.includes("พ.ร.บ")) {
            // Remove the word "กฎหมาย" from the text
            text = text.replace("กฎหมาย", "");

            // Update the text content of the div
            div.textContent = text;
        }
    });
}

// Call the function to remove the word from all matching divs
removeWordFromAllDivs();