import { sendDataToAWS } from './awsUploader.js';
import { GazeDataCollector } from './app.js'; // Importing GazeDataCollector properly

// Define the quiz data with questions, answers, and correct answers
const quizData = [
    {
        image: 'images/dog.jpg',  // Ensure this file exists in the correct directory
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Dog'
    },
    {
        image: 'images/cat.jpg',
        answers: ['Dog', 'Cat', 'Elephant', 'Horse', 'Rabbit', "I don't know"],
        correct: 'Cat'
    }
];


let currentQuestion = 0;
let score = 0;
const totalQuestions = quizData.length;
const gazeDataCollector = new GazeDataCollector();

// Get elements from DOM
const progressBar = document.getElementById('progressBar');
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
const progressContainer = document.getElementById('progressContainer');
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
    progressContainer.style.display = 'block';

    loadQuestion();
}

function loadQuestion() {
    const currentData = quizData[currentQuestion];

    questionImage.src = currentData.image;

    currentData.answers.forEach((answer, index) => {
        answerButtons[index].innerText = answer;
        answerButtons[index].onclick = () => checkAnswer(answer);
    });

    // Reset and start tracking gaze data for the new question
    gazeDataCollector.reset();
    gazeDataCollector.startTracking();
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
        updateProgressBar();
    } else {
        finishQuiz();
    }
}

function updateProgressBar() {
    const progress = (currentQuestion / totalQuestions) * 100;
    progressBar.style.width = progress + '%';
}

function finishQuiz() {
    alert(`Quiz completed! Your score is ${score} out of ${totalQuestions}.`);
}

document.addEventListener('DOMContentLoaded', initializeQuiz);
