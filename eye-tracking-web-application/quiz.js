import { sendDataToAWS } from './awsUploader.js';
import { GazeDataCollector } from './app.js'; // Importing GazeDataCollector properly

// Define the quiz data with questions, answers, and correct answers
const quizData = [
    {
        image: 'images/0001.png',  // Ensure this file exists in the correct directory
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Dog'
    },
    {
        image: 'images/0002.png',
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Cat'
    },
    {
        image: 'images/0003.png',  // Ensure this file exists in the correct directory
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Dog'
    },
    {
        image: 'images/0004.png',
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Cat'
    },
    {
        image: 'images/0005.png',  // Ensure this file exists in the correct directory
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Dog'
    },
    {
        image: 'images/0006.png',
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Cat'
    },
    {
        image: 'images/0007.png',  // Ensure this file exists in the correct directory
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Dog'
    },
    {
        image: 'images/0008.png',
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Cat'
    },
    {
        image: 'images/0009.png',
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Dog'
    },
    {
        image: 'images/0010.png',
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Cat'
    },
];

let currentQuestion = 0;
let score = 0;
const totalQuestions = quizData.length;
const gazeDataCollector = new GazeDataCollector();

// Get elements from DOM
const questionImage = document.getElementById('questionImage');
const answerButtons = [
    document.getElementById('answer1'),
    document.getElementById('answer2'),
    document.getElementById('answer3'),
    document.getElementById('answer4'),
    document.getElementById('answer5'),
    document.getElementById('answer6')
];
const quizContainer = document.getElementById('quizContainer');
const quizTitle = document.getElementById('quizTitle');
const startQuizButton = document.getElementById('startQuizButton');
const completionScreen = document.getElementById('completionScreen'); // For hiding after quiz starts

function initializeQuiz() {
    // Initialize gaze tracking
    gazeDataCollector.init();

    // Start the quiz
    startQuizButton.addEventListener('click', startQuiz);
}

function startQuiz() {
    completionScreen.style.display = 'none';
    startQuizButton.style.display = 'none';

    quizTitle.style.display = 'block';
    quizContainer.style.display = 'block';

    loadQuestion();
}

function loadQuestion() {
    const currentData = quizData[currentQuestion];

    // Hide answer buttons initially
    answerButtons.forEach(button => button.style.display = 'none');

    // Display the image and reset size to take up the entire page
    questionImage.src = currentData.image;
    questionImage.style.display = 'block';
    questionImage.style.width = '100vw';  // Full viewport width
    questionImage.style.height = '100vh'; // Full viewport height

    // Reset and start tracking gaze data for the new question
    gazeDataCollector.reset();
    gazeDataCollector.startTracking();

    // Display the image for 7 seconds, then hide the image and show the answer buttons
    setTimeout(() => {
        // Hide the image after 7 seconds
        questionImage.style.display = 'none';

        // Show answer buttons and assign click handlers
        currentData.answers.forEach((answer, index) => {
            answerButtons[index].innerText = answer;
            answerButtons[index].style.display = 'block';  // Show the answer buttons
            answerButtons[index].onclick = () => checkAnswer(answer);
        });
    }, 10000); // 7 seconds delay before showing the questions
}

function checkAnswer(answer) {
    const currentData = quizData[currentQuestion];

    // Stop tracking and send gaze data to AWS for the current question
    gazeDataCollector.stopTracking();

    const dataToSend = {
        body: JSON.stringify({
            question: currentQuestion,
            answerGiven: answer,
            correctAnswer: currentData.correct,
            gazeTracking: gazeDataCollector.getCollectedData(),
        })
    };

    sendDataToAWS(dataToSend);

    // Move to the next question
    currentQuestion++;
    if (currentQuestion < totalQuestions) {
        loadQuestion();
    } else {
        finishQuiz();
    }
}



function finishQuiz() {
    alert(`Quiz completed! Your score is ${score} out of ${totalQuestions}.`);
}

document.addEventListener('DOMContentLoaded', initializeQuiz);
