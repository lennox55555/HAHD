import { sendDataToAWS } from './awsUploader.js';
import { GazeDataCollector } from './app.js';

let quizData = [];
let score = 0;
const gazeDataCollector = new GazeDataCollector();

// Get elements from DOM
const questionImage = document.getElementById('questionImage');
const imageContainer = document.getElementById('imageContainer');
const answerContainer = document.getElementById('answerContainer');
const questionText = document.getElementById('questionText');
const answerButtons = Array.from({ length: 10 }, (_, i) => document.getElementById(`answer${i + 1}`));
const quizContainer = document.getElementById('quizContainer');
const quizTitle = document.getElementById('quizTitle');
const startQuizButton = document.getElementById('startQuizButton');
const completionScreen = document.getElementById('completionScreen');

// Load quiz data from the JSON file
function loadQuizData() {
    return fetch('quizData.json')
        .then(response => response.json())
        .then(data => {
            quizData = data;
            initializeQuiz();
        })
        .catch(error => {
            console.error('Error loading quiz data:', error);
        });
}

function initializeQuiz() {
    gazeDataCollector.init();
    startQuizButton.addEventListener('click', startQuiz);
    addHoverEffects();
}

function addHoverEffects() {
    answerButtons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            answerButtons.forEach(btn => {
                if (btn !== button) {
                    btn.style.opacity = '0.5';
                }
            });
        });
        button.addEventListener('mouseleave', () => {
            answerButtons.forEach(btn => {
                btn.style.opacity = '1';
            });
        });
    });
}

function startQuiz() {
    completionScreen.style.display = 'none';
    startQuizButton.style.display = 'none';
    quizTitle.style.display = 'none';
    quizContainer.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    loadRandomQuestion();
}

function loadRandomQuestion() {
    const randomIndex = Math.floor(Math.random() * quizData.length);
    const currentData = quizData[randomIndex];

    // Reset display
    imageContainer.style.display = 'flex';
    answerContainer.style.display = 'none';
    questionText.style.display = 'none';
    answerButtons.forEach(button => button.style.display = 'none');

    questionImage.src = currentData.image;
    questionImage.style.display = 'block';

    // Start eye tracking
    gazeDataCollector.startTracking();

    // Set timeout to hide image, stop tracking, and show answers
    setTimeout(() => {
        imageContainer.style.display = 'none';
        answerContainer.style.display = 'flex';
        questionText.style.display = 'block';
        questionText.textContent = "On a scale of 1-10, 1 being stop immediately or remain stopped, 5 being drive with caution, and 10 being continue driving. Given the previous driving environment (pedestrians, other cars, stoplights), how should the vehicle proceed?";
        gazeDataCollector.stopTracking();

        answerButtons.forEach((button, index) => {
            button.style.display = 'block';
            button.onclick = () => recordAnswer(index + 1, randomIndex);
        });
    }, 10000);
}


async function recordAnswer(answer, randomIndex) {
    const currentData = quizData[randomIndex];
    const collectedData = gazeDataCollector.getCollectedData();

    // Provide visual feedback for the selected button
    const selectedButton = document.getElementById(`answer${answer}`);
    selectedButton.classList.add('selected');

    // Disable all buttons to prevent multiple selections
    answerButtons.forEach(button => {
        button.disabled = true;
    });

    // Prepare data to send to AWS
    const dataToSend = {
        questionImage: currentData.image,
        selectedAnswer: answer,
        gazeData: collectedData.gazeData,
        timestamp: collectedData.timestamp
    };

    // Send data to AWS
    try {
        await sendDataToAWS({ body: dataToSend });
        console.log('Data successfully sent to AWS');
    } catch (error) {
        console.error('Error sending data to AWS:', error);
    }

    setTimeout(() => {
        // Remove the 'selected' class from the button
        selectedButton.classList.remove('selected');

        // Re-enable all buttons
        answerButtons.forEach(button => {
            button.disabled = false;
        });

        if (quizData.length > 0) {
            loadRandomQuestion();
        } else {
            finishQuiz();
        }
    }, 1000);
}

function finishQuiz() {
    quizContainer.style.display = 'none';
    completionScreen.style.display = 'block';
    document.getElementById('finalScore').textContent = "Thank you for completing the survey!";
}

document.addEventListener('DOMContentLoaded', loadQuizData);
