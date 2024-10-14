import { sendDataToAWS } from './awsUploader.js';

export class GazeDataCollector {
    constructor() {
        this.gazeData = [];
        this.trackingInterval = null;
        this.isTracking = false;
    }

    init() {
        webgazer
            .setRegression('ridge')
            .setGazeListener((data, elapsedTime) => {
                if (data && this.isTracking) {
                    this.collectGazeData(data.x, data.y);
                }
            })
            .begin();

        webgazer.showVideo(false);
        webgazer.showFaceOverlay(false);
        webgazer.showFaceFeedbackBox(false);
    }

    startTracking() {
        this.isTracking = true;
        this.gazeData = [];
        this.trackingInterval = setInterval(() => {
            webgazer.getCurrentPrediction().then(prediction => {
                if (prediction) {
                    this.collectGazeData(prediction.x, prediction.y);
                }
            });
        }, 100); // Every 100ms (1/10th of a second)
    }

    stopTracking() {
        this.isTracking = false;
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }
    }

    collectGazeData(x, y) {
        this.gazeData.push({ x, y, time: Date.now() });
    }

    getCollectedData() {
        return {
            gazeData: this.gazeData,
            timestamp: Date.now(),
        };
    }
}

// Helper function for throttling mouse movements
function throttle(func, limit) {
    let lastFunc;
    let lastRan;
    return function (...args) {
        const context = this;
        if (!lastRan) {
            func.apply(context, args);
            lastRan = Date.now();
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(function () {
                if (Date.now() - lastRan >= limit) {
                    func.apply(context, args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    };
}

class CacheManager {
    constructor() {
        // Initialization can go here if needed
    }

    // Method to clear local storage
    clearLocalStorage() {
        localStorage.clear();
        console.log("Local storage cleared.");
    }

    // Method to clear session storage
    clearSessionStorage() {
        sessionStorage.clear();
        console.log("Session storage cleared.");
    }

    // Method to clear all cookies
    clearCookies() {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            const eqPos = cookie.indexOf("=");
            const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
            // Set the cookie's expiration to a past date to delete it
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;";
        }

        console.log("All cookies cleared.");
    }

    // Method to unregister service workers
    clearServiceWorkers() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then((registrations) => {
                for (let registration of registrations) {
                    registration.unregister(); // Unregister each service worker
                    console.log("Service worker unregistered:", registration);
                }
            }).catch((error) => {
                console.error("Error unregistering service workers:", error);
            });
        }
    }

    // Method to clear everything at once (storage, cookies, and service workers)
    clearAllCaches() {
        this.clearLocalStorage();
        this.clearSessionStorage();
        this.clearCookies();
        this.clearServiceWorkers();
    }
}

class EyeTrackingApp {
    constructor() {
        this.gazeDataCollector = new GazeDataCollector();
        this.cacheManager = new CacheManager();  // Initialize the CacheManager
        this.totalClicks = 0;
        this.maxClicks = 5; // Set the number of clicks for calibration
        this.dotSize = 80; // Increased size for visibility of number
        this.timer = 0;
        this.interval = null;

        // Bind methods
        this.startApp = this.startApp.bind(this);
        this.calibrate = this.calibrate.bind(this);
        this.placeNextDot = this.placeNextDot.bind(this);
        this.endCalibration = this.endCalibration.bind(this);
    }

    startApp() {
        // Clear all caches, cookies, and service workers when the app starts
        this.cacheManager.clearAllCaches();

        document.getElementById('startButton').addEventListener('click', () => {
            document.getElementById('startScreen').style.display = 'none';

            this.createDot();
            this.placeNextDot();

        });
    }

    createDot() {
        let dot = document.querySelector('.calibration-button');
        if (!dot) {
            dot = document.createElement('button');
            dot.classList.add('calibration-button');
            document.body.appendChild(dot);
        }
    }

    placeNextDot() {
        const dot = document.querySelector('.calibration-button');
        const randomX = Math.floor(Math.random() * (window.innerWidth - this.dotSize));
        const randomY = Math.floor(Math.random() * (window.innerHeight - this.dotSize));

        dot.style.position = 'absolute';
        dot.style.left = `${randomX}px`;
        dot.style.top = `${randomY}px`;
        dot.style.backgroundColor = 'red';
        dot.disabled = false;

        // Set the inner text of the dot to the remaining clicks
        let remainingClicks = this.maxClicks - this.totalClicks;
        dot.innerText = remainingClicks;

        // Add the click handler
        dot.onclick = () => this.calibrate(randomX + this.dotSize / 2, randomY + this.dotSize / 2);
    }

    calibrate(screenX, screenY) {
        this.totalClicks += 1;
        webgazer.recordScreenPosition(screenX, screenY);

        const dot = document.querySelector('.calibration-button');

        // Trigger the pop animation
        dot.classList.add('pop-animation');

        // Remove the animation class after the animation ends
        dot.addEventListener('animationend', () => {
            dot.classList.remove('pop-animation');
        });

        // Check if the user has reached the max number of clicks
        if (this.totalClicks >= this.maxClicks) {
            this.endCalibration();
        } else {
            setTimeout(() => {
                this.placeNextDot(); // Place the next dot after animation
            }, 200);  // Slight delay to match animation time
        }
    }




    endCalibration() {
        clearInterval(this.interval);
        const dot = document.querySelector('.calibration-button');
        if (dot) dot.style.display = 'none';
        document.getElementById('completionScreen').style.display = 'block';

        this.gazeDataCollector.init();
        this.gazeDataCollector.startTracking();
    }
}

window.onload = function () {
    const app = new EyeTrackingApp();
    app.startApp();
};
